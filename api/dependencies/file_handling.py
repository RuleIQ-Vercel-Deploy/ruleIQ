"""File handling dependencies for API endpoints.

This module provides typed helpers for file upload, download, and processing
operations in API endpoints.
"""
from __future__ import annotations

import os
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
from fastapi import UploadFile, HTTPException, status
from config.logging_config import get_logger

logger = get_logger(__name__)

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.csv', '.json', '.xlsx'}
UPLOAD_DIR = Path("uploads")


def validate_file_upload(file: UploadFile) -> None:
    """
    Validate uploaded file for size and type.
    
    Args:
        file: The uploaded file to validate
        
    Raises:
        HTTPException: If file validation fails
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (if available)
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
        )


async def save_upload_file(
    upload_file: UploadFile,
    destination: Optional[Path] = None,
    create_hash: bool = True
) -> Dict[str, Any]:
    """
    Save an uploaded file to disk.
    
    Args:
        upload_file: The file to save
        destination: Optional destination path
        create_hash: Whether to create a hash of the file
        
    Returns:
        Dictionary with file metadata including path and optional hash
    """
    validate_file_upload(upload_file)
    
    # Create upload directory if it doesn't exist
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    # Generate destination path if not provided
    if destination is None:
        file_ext = Path(upload_file.filename).suffix if upload_file.filename else ""
        destination = UPLOAD_DIR / f"{os.urandom(16).hex()}{file_ext}"
    
    # Calculate hash if requested
    file_hash = None
    if create_hash:
        hasher = hashlib.sha256()
    
    # Write file to disk
    try:
        with open(destination, "wb") as buffer:
            while chunk := await upload_file.read(8192):
                buffer.write(chunk)
                if create_hash:
                    hasher.update(chunk)
        
        if create_hash:
            file_hash = hasher.hexdigest()
        
        return {
            "filename": upload_file.filename,
            "path": str(destination),
            "size": destination.stat().st_size,
            "hash": file_hash,
            "content_type": upload_file.content_type
        }
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        if destination.exists():
            destination.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file"
        )


def cleanup_old_files(directory: Path = UPLOAD_DIR, days_old: int = 7) -> int:
    """
    Clean up old files from the upload directory.
    
    Args:
        directory: Directory to clean
        days_old: Age threshold in days
        
    Returns:
        Number of files deleted
    """
    import time
    
    if not directory.exists():
        return 0
    
    current_time = time.time()
    age_seconds = days_old * 24 * 60 * 60
    deleted_count = 0
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > age_seconds:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete file {file_path}: {e}")
    
    return deleted_count


__all__ = [
    "validate_file_upload",
    "save_upload_file",
    "cleanup_old_files",
    "MAX_FILE_SIZE",
    "ALLOWED_EXTENSIONS",
    "UPLOAD_DIR"
]