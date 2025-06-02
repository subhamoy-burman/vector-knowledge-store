"""
Azure Blob Storage service for storing document files.
"""
import os
import logging
from typing import Dict, Optional

from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError

from config.settings import AZURE_STORAGE_CONNECTION_STRING, BLOB_CONTAINER_NAME

logger = logging.getLogger(__name__)

class BlobStorageService:
    """Service for Azure Blob Storage operations."""
    
    def __init__(self):
        """Initialize the Azure Blob Storage client."""
        self.connection_string = AZURE_STORAGE_CONNECTION_STRING
        self.container_name = BLOB_CONTAINER_NAME
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self._ensure_container_exists()
    
    def _ensure_container_exists(self) -> None:
        """Ensure the blob container exists, create if it doesn't."""
        try:
            container_client = self.blob_service_client.create_container(self.container_name)
            logger.info(f"Container '{self.container_name}' created.")
        except ResourceExistsError:
            logger.info(f"Container '{self.container_name}' already exists.")
    
    def upload_file(self, file_path: str) -> Dict[str, str]:
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            Dictionary with blob metadata
        """
        try:
            file_name = os.path.basename(file_path)
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_name
            )
            
            # Set content type based on file extension
            content_type = self._get_content_type(file_path)
            content_settings = ContentSettings(content_type=content_type)
            
            # Upload the file
            with open(file_path, "rb") as data:
                blob_client.upload_blob(
                    data, 
                    overwrite=True,
                    content_settings=content_settings
                )
            
            logger.info(f"Uploaded file '{file_name}' to container '{self.container_name}'")
            
            return {
                "blob_url": blob_client.url,
                "container": self.container_name,
                "blob_name": file_name
            }
            
        except Exception as e:
            logger.error(f"Error uploading file to Blob Storage: {e}")
            raise
    
    def list_blobs(self) -> list:
        """
        List all blobs in the container.
        
        Returns:
            List of blob names
        """
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs = []
        
        for blob in container_client.list_blobs():
            blobs.append(blob.name)
            
        return blobs
    
    def delete_blob(self, blob_name: str) -> None:
        """
        Delete a blob from the container.
        
        Args:
            blob_name: Name of the blob to delete
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"Deleted blob '{blob_name}' from container '{self.container_name}'")
        except Exception as e:
            logger.error(f"Error deleting blob: {e}")
            raise
    
    def _get_content_type(self, file_path: str) -> str:
        """
        Get content type based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Content type string
        """
        extension = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.csv': 'text/csv'
        }
        
        return content_types.get(extension, 'application/octet-stream')