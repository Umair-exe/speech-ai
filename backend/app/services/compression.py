import os
import uuid
import subprocess
from PIL import Image
from typing import Dict, Optional
import aiofiles
from fastapi import UploadFile, HTTPException
from pathlib import Path


class CompressionService:
    """Service for image compression"""
    
    def __init__(self):
        self.temp_dir = "./temp"
        self.output_dir = "./compressed"
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def compress_image(
        self,
        file: UploadFile,
        quality: int = 85,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        output_format: Optional[str] = None
    ) -> Dict:
        """
        Compress an image file
        
        Args:
            file: Uploaded image file
            quality: JPEG quality (1-100), default 85
            max_width: Maximum width in pixels (maintains aspect ratio)
            max_height: Maximum height in pixels (maintains aspect ratio)
            output_format: Output format (jpeg, png, webp). Default: same as input
            
        Returns:
            Dict with compression results
        """
        # Validate quality
        if not 1 <= quality <= 100:
            raise HTTPException(status_code=400, detail="Quality must be between 1 and 100")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file temporarily
        temp_path = await self._save_temp_file(file)
        
        try:
            # Open image
            img = Image.open(temp_path)
            original_size = os.path.getsize(temp_path)
            original_dimensions = img.size
            original_format = img.format
            
            # Convert RGBA to RGB if needed for JPEG
            if img.mode == 'RGBA' and (output_format == 'jpeg' or output_format == 'jpg'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                img = rgb_img
            
            # Resize if dimensions specified
            if max_width or max_height:
                img = self._resize_image(img, max_width, max_height)
            
            # Determine output format
            if not output_format:
                output_format = original_format.lower() if original_format else 'jpeg'
            
            # Generate output filename
            output_filename = f"{uuid.uuid4()}.{output_format}"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Save compressed image
            save_kwargs = {}
            if output_format in ['jpeg', 'jpg']:
                save_kwargs = {
                    'format': 'JPEG',
                    'quality': quality,
                    'optimize': True
                }
            elif output_format == 'png':
                save_kwargs = {
                    'format': 'PNG',
                    'optimize': True,
                    'compress_level': max(0, min(9, (100 - quality) // 11))
                }
            elif output_format == 'webp':
                save_kwargs = {
                    'format': 'WEBP',
                    'quality': quality,
                    'method': 6  # Best compression
                }
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {output_format}")
            
            img.save(output_path, **save_kwargs)
            
            # Get compressed file stats
            compressed_size = os.path.getsize(output_path)
            compressed_dimensions = img.size
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            # Clean up temp file
            os.remove(temp_path)
            
            return {
                "success": True,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": round(compression_ratio, 2),
                "original_dimensions": {
                    "width": original_dimensions[0],
                    "height": original_dimensions[1]
                },
                "compressed_dimensions": {
                    "width": compressed_dimensions[0],
                    "height": compressed_dimensions[1]
                },
                "output_format": output_format,
                "output_file": output_filename,
                "output_path": output_path,
                "quality": quality
            }
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")
    
    async def _save_temp_file(self, file: UploadFile) -> str:
        """Save uploaded file to temporary location"""
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_path = os.path.join(self.temp_dir, temp_filename)
        
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        await file.seek(0)  # Reset file pointer
        return temp_path
    
    def _resize_image(
        self,
        img: Image.Image,
        max_width: Optional[int],
        max_height: Optional[int]
    ) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        original_width, original_height = img.size
        
        # Calculate new dimensions
        if max_width and max_height:
            # Fit within both dimensions
            ratio = min(max_width / original_width, max_height / original_height)
        elif max_width:
            ratio = max_width / original_width
        elif max_height:
            ratio = max_height / original_height
        else:
            return img
        
        # Only downscale, never upscale
        if ratio >= 1:
            return img
        
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def get_compressed_file(self, filename: str) -> str:
        """Get path to compressed file"""
        path = os.path.join(self.output_dir, filename)
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Compressed file not found")
        return path
    
    def cleanup_file(self, filename: str) -> bool:
        """Delete a compressed file"""
        path = os.path.join(self.output_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
    
    async def compress_video(
        self,
        file: UploadFile,
        quality: str = "medium",
        max_width: Optional[int] = None,
        output_format: str = "mp4"
    ) -> Dict:
        """
        Compress a video file using ffmpeg
        
        Args:
            file: Uploaded video file
            quality: Compression quality preset (low, medium, high)
            max_width: Maximum width in pixels (maintains aspect ratio)
            output_format: Output format (mp4, webm, avi)
            
        Returns:
            Dict with compression results
        """
        # Validate file type
        video_types = ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo', 
                       'video/webm', 'video/x-matroska']
        if not file.content_type or file.content_type not in video_types:
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Quality presets for CRF (Constant Rate Factor)
        # Lower CRF = higher quality, larger file
        quality_presets = {
            "low": 28,      # Smaller file, lower quality
            "medium": 23,   # Balanced
            "high": 18      # Larger file, higher quality
        }
        
        crf = quality_presets.get(quality, 23)
        
        # Save uploaded file temporarily
        temp_path = await self._save_temp_file(file)
        
        try:
            # Get original file stats
            original_size = os.path.getsize(temp_path)
            
            # Get video info using ffprobe
            probe_cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,duration',
                '-of', 'json',
                temp_path
            ]
            
            try:
                probe_result = subprocess.run(
                    probe_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                import json
                video_info = json.loads(probe_result.stdout)
                original_width = video_info['streams'][0].get('width', 0)
                original_height = video_info['streams'][0].get('height', 0)
                duration = video_info['streams'][0].get('duration', '0')
            except Exception as e:
                print(f"Warning: Could not get video info: {e}")
                original_width = 0
                original_height = 0
                duration = '0'
            
            # Generate output filename
            output_filename = f"{uuid.uuid4()}.{output_format}"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Build ffmpeg command
            ffmpeg_cmd = [
                'ffmpeg', '-i', temp_path,
                '-c:v', 'libx264',  # Video codec
                '-crf', str(crf),   # Quality
                '-preset', 'medium', # Encoding speed
                '-c:a', 'aac',      # Audio codec
                '-b:a', '128k',     # Audio bitrate
            ]
            
            # Add scaling if max_width specified
            if max_width and original_width > max_width:
                ffmpeg_cmd.extend(['-vf', f'scale={max_width}:-2'])
            
            # Output file
            ffmpeg_cmd.extend(['-y', output_path])  # -y to overwrite
            
            # Run ffmpeg compression
            print(f"Compressing video with command: {' '.join(ffmpeg_cmd)}")
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown ffmpeg error"
                raise HTTPException(
                    status_code=500,
                    detail=f"Video compression failed: {error_msg}"
                )
            
            # Get compressed file stats
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            # Clean up temp file
            os.remove(temp_path)
            
            return {
                "success": True,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": round(compression_ratio, 2),
                "original_dimensions": {
                    "width": original_width,
                    "height": original_height
                },
                "duration": duration,
                "output_format": output_format,
                "output_file": output_filename,
                "output_path": output_path,
                "quality": quality
            }
            
        except HTTPException:
            raise
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(status_code=500, detail=f"Video compression failed: {str(e)}")


# Global instance
compression_service = CompressionService()
