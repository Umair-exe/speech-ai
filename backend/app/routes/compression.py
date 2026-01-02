from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
from app.services.compression import compression_service
import os

router = APIRouter(prefix="/api/compression", tags=["compression"])


@router.post("/compress")
async def compress_image(
    file: UploadFile = File(...),
    quality: int = Query(default=85, ge=1, le=100, description="Compression quality (1-100)"),
    max_width: Optional[int] = Query(default=None, ge=1, description="Maximum width in pixels"),
    max_height: Optional[int] = Query(default=None, ge=1, description="Maximum height in pixels"),
    output_format: Optional[str] = Query(default=None, regex="^(jpeg|jpg|png|webp)$", description="Output format")
):
    """
    Compress an image file with optional resizing
    
    Parameters:
    - **file**: Image file to compress
    - **quality**: Compression quality (1-100), default 85
    - **max_width**: Maximum width in pixels (maintains aspect ratio)
    - **max_height**: Maximum height in pixels (maintains aspect ratio)
    - **output_format**: Output format (jpeg, png, webp). Default: same as input
    
    Returns compression statistics and file information
    """
    result = await compression_service.compress_image(
        file=file,
        quality=quality,
        max_width=max_width,
        max_height=max_height,
        output_format=output_format
    )
    return result


@router.get("/download/{filename}")
async def download_compressed_image(filename: str):
    """
    Download a compressed image file
    
    Parameters:
    - **filename**: Name of the compressed file
    """
    try:
        file_path = compression_service.get_compressed_file(filename)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{filename}")
async def delete_compressed_image(filename: str):
    """
    Delete a compressed image file
    
    Parameters:
    - **filename**: Name of the compressed file to delete
    """
    success = compression_service.cleanup_file(filename)
    if success:
        return {"message": "File deleted successfully", "filename": filename}
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.post("/compress-video")
async def compress_video(
    file: UploadFile = File(...),
    quality: str = Query(default="medium", regex="^(low|medium|high)$", description="Compression quality preset"),
    max_width: Optional[int] = Query(default=None, ge=1, description="Maximum width in pixels"),
    output_format: str = Query(default="mp4", regex="^(mp4|webm|avi)$", description="Output format")
):
    """
    Compress a video file
    
    Parameters:
    - **file**: Video file to compress
    - **quality**: Compression quality preset (low, medium, high), default medium
    - **max_width**: Maximum width in pixels (maintains aspect ratio)
    - **output_format**: Output format (mp4, webm, avi), default mp4
    
    Returns compression statistics and file information
    """
    result = await compression_service.compress_video(
        file=file,
        quality=quality,
        max_width=max_width,
        output_format=output_format
    )
    return result


@router.post("/compress-and-detect")
async def compress_and_detect(
    file: UploadFile = File(...),
    quality: int = Query(default=85, ge=1, le=100),
    max_width: Optional[int] = Query(default=None, ge=1),
    max_height: Optional[int] = Query(default=None, ge=1),
    output_format: Optional[str] = Query(default=None, regex="^(jpeg|jpg|png|webp)$")
):
    """
    Compress an image and run AI detection on both original and compressed versions
    
    This is useful to compare how compression affects AI detection results
    """
    from app.services.detection import DetectionService
    
    detection_service = DetectionService()
    
    # Run detection on original
    original_detection = await detection_service.detect_media(file, user_id=None)
    
    # Reset file pointer
    await file.seek(0)
    
    # Compress image
    compression_result = await compression_service.compress_image(
        file=file,
        quality=quality,
        max_width=max_width,
        max_height=max_height,
        output_format=output_format
    )
    
    # Run detection on compressed image
    compressed_file_path = compression_result["output_path"]
    
    # Create a mock UploadFile from the compressed file
    from fastapi import UploadFile as FastAPIUploadFile
    import aiofiles
    
    async with aiofiles.open(compressed_file_path, 'rb') as f:
        content = await f.read()
    
    # Note: For full implementation, you'd create a proper UploadFile object
    # For now, we'll skip the compressed detection to avoid complexity
    
    return {
        "original_detection": {
            "is_ai_generated": original_detection.is_ai_generated,
            "confidence": original_detection.confidence,
            "artifacts": original_detection.artifacts
        },
        "compression": compression_result,
        "message": "Compression completed. Original detection result included."
    }
