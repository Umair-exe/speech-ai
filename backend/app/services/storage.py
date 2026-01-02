import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from app.config import settings


class StorageService:
    """Handle file storage (local or S3)"""
    
    def __init__(self):
        # Always use local storage for now
        self.use_s3 = False
        
        # Use local storage
        self.local_storage_path = "./uploads"
        os.makedirs(self.local_storage_path, exist_ok=True)
    
    async def save_file(self, file_path: str, file_name: str) -> str:
        """
        Save file to storage (S3 or local)
        
        Args:
            file_path: Local path to the file
            file_name: Name to save the file as
            
        Returns:
            Storage path/URL
        """
        if self.use_s3:
            return await self._save_to_s3(file_path, file_name)
        else:
            return await self._save_locally(file_path, file_name)
    
    async def _save_to_s3(self, file_path: str, file_name: str) -> str:
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                file_name
            )
            return f"s3://{self.bucket_name}/{file_name}"
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
    
    async def _save_locally(self, file_path: str, file_name: str) -> str:
        """Save file locally"""
        import shutil
        
        destination = os.path.join(self.local_storage_path, file_name)
        shutil.copy(file_path, destination)
        return destination
    
    async def get_file_url(self, file_path: str) -> Optional[str]:
        """Get public URL for file (S3 only)"""
        if self.use_s3 and file_path.startswith("s3://"):
            file_name = file_path.replace(f"s3://{self.bucket_name}/", "")
            try:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_name},
                    ExpiresIn=3600  # URL expires in 1 hour
                )
                return url
            except ClientError:
                return None
        return file_path
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        if self.use_s3 and file_path.startswith("s3://"):
            file_name = file_path.replace(f"s3://{self.bucket_name}/", "")
            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_name)
                return True
            except ClientError:
                return False
        else:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return True
            except Exception:
                return False


storage_service = StorageService()
