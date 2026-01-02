"""OCR routes for text extraction from images."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import logging
import io
from datetime import datetime
import os
from pathlib import Path

from ..services.ocr import extract_text_from_image, is_image_file, translate_image_text
from ..services.translation import simple_translate

router = APIRouter(prefix="/api/ocr", tags=["OCR"])
logger = logging.getLogger(__name__)

# Create translated_images directory if it doesn't exist
TRANSLATED_IMAGES_DIR = Path("translated_images")
TRANSLATED_IMAGES_DIR.mkdir(exist_ok=True)

@router.post("/extract")
async def extract_text_from_image_route(
    file: UploadFile = File(...),
    language: str = "eng"
):
    """
    Extract text from an uploaded image using OCR.
    
    Parameters:
    - file: Image file (jpg, png, gif, bmp, tiff, webp)
    - language: OCR language code (default: 'eng' for English)
    
    Returns:
    - extracted_text: The text extracted from the image
    - filename: Original filename
    - success: Success status
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not is_image_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file (jpg, png, gif, bmp, tiff, webp)"
            )
        
        # Read file content
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(contents) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {max_size / (1024*1024)}MB"
            )
        
        # Extract text from image
        extracted_text = await extract_text_from_image(contents, language)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "extracted_text": extracted_text,
                "filename": file.filename,
                "character_count": len(extracted_text),
                "language": language
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")


@router.get("/supported-languages")
async def get_supported_ocr_languages():
    """
    Get list of supported OCR languages.
    
    Returns:
    - List of supported language codes
    """
    # Common Tesseract language codes
    languages = [
        {"code": "eng", "name": "English"},
        {"code": "spa", "name": "Spanish"},
        {"code": "fra", "name": "French"},
        {"code": "deu", "name": "German"},
        {"code": "ita", "name": "Italian"},
        {"code": "por", "name": "Portuguese"},
        {"code": "rus", "name": "Russian"},
        {"code": "jpn", "name": "Japanese"},
        {"code": "chi_sim", "name": "Chinese (Simplified)"},
        {"code": "chi_tra", "name": "Chinese (Traditional)"},
        {"code": "ara", "name": "Arabic"},
        {"code": "hin", "name": "Hindi"},
        {"code": "kor", "name": "Korean"},
        {"code": "urd", "name": "Urdu"},
        {"code": "hun", "name": "Hungarian"},
    ]
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "languages": languages
        }
    )


@router.post("/translate-image")
async def translate_image_route(
    file: UploadFile = File(...),
    source_lang: str = "en",
    target_lang: str = "es"
):
    """
    Translate text in an image and return a new image with translated text.
    
    Parameters:
    - file: Image file (jpg, png, gif, bmp, tiff, webp)
    - source_lang: Source language code (e.g., 'en', 'es', 'fr')
    - target_lang: Target language code (e.g., 'en', 'es', 'fr')
    
    Returns:
    - Modified image with translated text
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not is_image_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file (jpg, png, gif, bmp, tiff, webp)"
            )
        
        # Read file content
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(contents) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {max_size / (1024*1024)}MB"
            )
        
        # Translate image text
        translated_image_bytes, original_text, translated_text = await translate_image_text(
            contents,
            source_lang,
            target_lang,
            simple_translate
        )
        
        # Save the translated image temporarily
        import uuid
        import base64
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"translated_{timestamp}_{unique_id}.png"
        filepath = TRANSLATED_IMAGES_DIR / filename
        
        with open(filepath, 'wb') as f:
            f.write(translated_image_bytes)
        
        # Convert image to base64 for response
        image_base64 = base64.b64encode(translated_image_bytes).decode('utf-8')
        
        # Return JSON with both image and text
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "image_base64": image_base64,
                "original_text": original_text,
                "translated_text": translated_text,
                "filename": filename,
                "source_language": source_lang,
                "target_language": target_lang
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image translation failed: {str(e)}")
