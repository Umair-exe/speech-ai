from fastapi import APIRouter, Form, HTTPException
from typing import Optional
from app.services.translation import translation_service

router = APIRouter(prefix="/api/translation", tags=["translation"])


@router.post("/translate")
async def translate_text(
    text: str = Form(..., description="Text to translate"),
    source_lang: str = Form("auto", description="Source language code (auto for auto-detection)"),
    target_lang: str = Form("en", description="Target language code")
):
    """
    Translate text from one language to another

    Parameters:
    - **text**: Text to translate
    - **source_lang**: Source language code (default: auto)
    - **target_lang**: Target language code (default: en)

    Returns translation result with original and translated text
    """
    result = await translation_service.translate_text(text, source_lang, target_lang)

    return {
        "success": True,
        "message": "Translation completed successfully",
        "data": result
    }


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for translation (filtered to only show OCR-supported languages)
    """
    # Only return languages that have OCR support
    ocr_supported_languages = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-cn': 'Chinese (Simplified)',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'ur': 'Urdu',
        'hu': 'Hungarian'
    }

    return {
        "success": True,
        "languages": [{"code": code, "name": name} for code, name in ocr_supported_languages.items()]
    }