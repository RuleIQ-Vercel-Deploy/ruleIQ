from fastapi import UploadFile, File, HTTPException, status
from typing import List, Optional, Tuple
import os
import hashlib
import re
import mimetypes
import time
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from config.settings import get_settings
from config.logging_config import get_logger

# Get logger first
settings = get_settings()
logger = get_logger(__name__)

# Try to import magic, but provide fallback if not available
try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not available. Using fallback MIME type detection.")


class ValidationResult(Enum):
    """Validation result status."""

    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    QUARANTINED = "quarantined"


@dataclass
class FileAnalysisReport:
    """Comprehensive file analysis report."""

    filename: str
    original_filename: str
    content_type: str
    detected_type: str
    file_size: int
    file_hash: str
    validation_result: ValidationResult
    security_score: float  # 0.0 (safe) to 1.0 (dangerous)
    threats_detected: List[str]
    recommendations: List[str]
    validation_time: float


# File signature mappings for additional security
FILE_SIGNATURES = {
    "application/pdf": [b"%PDF"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/gif": [b"GIF87a", b"GIF89a"],
    "application/zip": [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [b"PK\x03\x04"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [b"PK\x03\x04"],
    "text/plain": None,  # Text files don't have signatures
    "text/csv": None,
}

# Dangerous filename patterns
DANGEROUS_PATTERNS = [
    r"\.\./",  # Path traversal
    r"\.\.\\",  # Windows path traversal
    r"[<>:|?*]",  # Invalid filename characters
    r"[\x00-\x1f\x7f]",  # Control characters
]

# Dangerous extensions even if MIME type seems safe
DANGEROUS_EXTENSIONS = [
    ".exe",
    ".dll",
    ".scr",
    ".bat",
    ".cmd",
    ".com",
    ".pif",
    ".js",
    ".vbs",
    ".jar",
    ".app",
    ".dmg",
    ".deb",
    ".rpm",
    ".sh",
    ".bash",
    ".ps1",
    ".psm1",
    ".msi",
    ".cab",
]

# Advanced threat patterns - byte sequences that indicate malicious content
MALWARE_BYTE_PATTERNS = [
    b"MZ\x90\x00",  # DOS/PE header
    b"\x7fELF",  # ELF executable
    b"\xca\xfe\xba\xbe",  # Mach-O (macOS)
    b"<?php",
    b"<%@",  # JSP
    b"<script",
    b"eval(",
    b"base64_decode",
    b"shell_exec",
    b"system(",
    b"exec(",
]


def detect_mime_type_fallback(file_content: bytes, filename: str = "") -> str:
    """
    Fallback MIME type detection when python-magic is not available.
    Uses file signatures and file extensions for detection.
    """
    if not file_content:
        return "application/octet-stream"

    # Check against known file signatures
    for mime_type, signatures in FILE_SIGNATURES.items():
        if signatures is not None:
            for signature in signatures:
                if file_content.startswith(signature):
                    return mime_type

    # Fallback to filename extension using mimetypes module
    if filename:
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type:
            return guessed_type

    # Try to detect text files
    try:
        file_content.decode("utf-8")
        # Check for common text formats
        if filename.lower().endswith(".csv"):
            return "text/csv"
        elif filename.lower().endswith(".json"):
            return "application/json"
        elif filename.lower().endswith(".xml"):
            return "application/xml"
        return "text/plain"
    except UnicodeDecodeError:
        pass

    # Default to octet-stream
    return "application/octet-stream"


def get_file_mime_type(file_content: bytes, filename: str = "") -> str:
    """
    Get MIME type using python-magic if available, otherwise use fallback detection.
    """
    if MAGIC_AVAILABLE:
        try:
            return magic.from_buffer(file_content, mime=True)
        except Exception as e:
            logger.warning(f"Magic detection failed: {e}, using fallback")
            return detect_mime_type_fallback(file_content, filename)
    else:
        return detect_mime_type_fallback(file_content, filename)


# File size limits by type (bytes)
TYPE_SIZE_LIMITS = {
    "image/jpeg": 10 * 1024 * 1024,  # 10MB
    "image/png": 10 * 1024 * 1024,  # 10MB
    "image/gif": 5 * 1024 * 1024,  # 5MB
    "application/pdf": 50 * 1024 * 1024,  # 50MB
    "text/csv": 10 * 1024 * 1024,  # 10MB
    "text/plain": 5 * 1024 * 1024,  # 5MB
}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent security issues."""
    # Remove any path components
    filename = os.path.basename(filename)

    # Replace dangerous characters
    filename = re.sub(r"[^\w\s.-]", "_", filename)

    # Remove multiple dots to prevent extension confusion
    filename = re.sub(r"\.{2,}", ".", filename)

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    filename = name + ext

    return filename


def validate_file_content(file_content: bytes, content_type: str, filename: str = "") -> bool:
    """Validate file content matches declared content type."""
    # Check file signatures if available
    signatures = FILE_SIGNATURES.get(content_type)
    if signatures is not None:
        if not any(file_content.startswith(sig) for sig in signatures):
            return False

    # Use python-magic for deep content inspection
    try:
        detected_type = get_file_mime_type(file_content, filename)
        # Allow some flexibility for related types
        if content_type.startswith("text/") and detected_type.startswith("text/"):
            return True
        if content_type != detected_type:
            logger.warning(
                f"Content type mismatch: declared={content_type}, detected={detected_type}"
            )
            return False
    except Exception as e:
        logger.error(f"Error detecting file type: {e}")
        return False

    return True


def check_for_malicious_content(file_content: bytes, filename: str) -> bool:
    """Check for potentially malicious content patterns."""
    # Check for dangerous extensions
    _, ext = os.path.splitext(filename.lower())
    if ext in DANGEROUS_EXTENSIONS:
        return False

    # Check for embedded executables in archives
    if file_content.startswith(b"PK"):  # ZIP-based files
        # Simple check for executable signatures within ZIP
        for pattern in MALWARE_BYTE_PATTERNS[:3]:  # Check executable patterns
            if pattern.encode() in file_content:
                logger.warning(f"Possible embedded executable in {filename}")
                return False

    # Check for suspicious patterns in text files
    if filename.endswith((".txt", ".csv", ".json", ".xml")):
        try:
            text_content = file_content.decode("utf-8", errors="ignore")
            # Check for script injections
            suspicious_patterns = [
                r"<script[^>]*>",
                r"javascript:",
                r"on\w+\s*=",  # Event handlers
                r"eval\s*\(",
                r"exec\s*\(",
            ]
            for pattern in suspicious_patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    logger.warning(f"Suspicious pattern found in {filename}")
                    return False
        except:
            pass

    return True


def analyze_file_comprehensively(
    file_content: bytes, filename: str, content_type: str
) -> FileAnalysisReport:
    """Perform comprehensive multi-layered file analysis."""
    start_time = time.time()
    threats_detected = []
    recommendations = []
    security_score = 0.0

    # Basic file info
    file_size = len(file_content)
    file_hash = calculate_file_hash(file_content)
    detected_type = get_file_mime_type(file_content, filename) if file_content else "unknown"
    safe_filename = sanitize_filename(filename)

    # Layer 1: File size validation by type
    max_size = TYPE_SIZE_LIMITS.get(content_type, settings.max_file_size)
    if file_size > max_size:
        threats_detected.append(f"File size ({file_size}) exceeds limit for type {content_type}")
        security_score += 0.3

    # Layer 2: MIME type mismatch detection
    if content_type != detected_type:
        threats_detected.append(
            f"MIME type mismatch: declared={content_type}, detected={detected_type}"
        )
        security_score += 0.4

    # Layer 3: Dangerous extension check
    _, ext = os.path.splitext(filename.lower())
    if ext in DANGEROUS_EXTENSIONS:
        threats_detected.append(f"Dangerous file extension: {ext}")
        security_score += 0.8

    # Layer 4: Malware pattern detection
    for pattern in MALWARE_BYTE_PATTERNS:
        if pattern.encode() in file_content:
            threats_detected.append(f"Malware pattern detected: {pattern}")
            security_score += 0.7

    # Layer 5: Content structure analysis
    if content_type.startswith("text/"):
        try:
            text_content = file_content.decode("utf-8", errors="ignore")

            # Check for obfuscated content
            if len(re.findall(r"[A-Za-z0-9+/]{50,}", text_content)) > 5:
                threats_detected.append("Possible base64-encoded content detected")
                security_score += 0.3

            # Check for URL patterns
            url_patterns = re.findall(r'https?://[^\s<>"{}|\^`\[\]]+', text_content)
            if len(url_patterns) > 10:
                threats_detected.append(f"High number of URLs detected: {len(url_patterns)}")
                security_score += 0.2

        except UnicodeDecodeError:
            threats_detected.append("Text file contains non-UTF8 content")
            security_score += 0.2

    # Layer 6: Archive inspection (ZIP-based files)
    if file_content.startswith(b"PK"):
        # Check for nested archives (zip bombs)
        pk_count = file_content.count(b"PK")
        if pk_count > 100:
            threats_detected.append(f"Possible zip bomb: {pk_count} PK signatures")
            security_score += 0.6

    # Layer 7: Image file validation
    if content_type.startswith("image/"):
        # Check for EXIF data anomalies
        if b"<?php" in file_content or b"<script" in file_content:
            threats_detected.append("Suspicious script content in image file")
            security_score += 0.8

        # Check for abnormal metadata size
        if content_type == "image/jpeg" and file_content[2:4] == b"\xff\xe1":
            exif_size = int.from_bytes(file_content[4:6], "big")
            if exif_size > 65535:  # Abnormally large EXIF
                threats_detected.append("Abnormally large EXIF metadata")
                security_score += 0.4

    # Determine validation result
    if security_score >= 0.8:
        validation_result = ValidationResult.MALICIOUS
    elif security_score >= 0.5:
        validation_result = ValidationResult.SUSPICIOUS
    elif security_score >= 0.2:
        validation_result = ValidationResult.QUARANTINED
    else:
        validation_result = ValidationResult.CLEAN

    # Generate recommendations
    if threats_detected:
        recommendations.append("File should be quarantined for manual review")
        if security_score >= 0.5:
            recommendations.append("Block file upload immediately")
        if "MIME type mismatch" in str(threats_detected):
            recommendations.append("Verify file type with multiple detection methods")
        if any("URL" in threat for threat in threats_detected):
            recommendations.append("Scan URLs for malicious domains")
    else:
        recommendations.append("File appears safe for upload")

    validation_time = time.time() - start_time

    return FileAnalysisReport(
        filename=safe_filename,
        original_filename=filename,
        content_type=content_type,
        detected_type=detected_type,
        file_size=file_size,
        file_hash=file_hash,
        validation_result=validation_result,
        security_score=min(security_score, 1.0),
        threats_detected=threats_detected,
        recommendations=recommendations,
        validation_time=validation_time,
    )


def get_file_validator(
    max_size: int = None,
    allowed_types: List[str] = None,
    enable_content_validation: bool = True,
    enable_malware_check: bool = True,
    security_level: str = "standard",  # "basic", "standard", "strict"
) -> callable:
    """Get a file validator with multi-layered security checks."""
    if max_size is None:
        max_size = settings.max_file_size
    if allowed_types is None:
        allowed_types = settings.allowed_file_types
        if isinstance(allowed_types, str):
            allowed_types = [allowed_types]

    async def validator(file: UploadFile = File(...)) -> Tuple[UploadFile, FileAnalysisReport]:
        # Layer 1: Basic validations
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the limit of {max_size / 1024 / 1024} MB",
            )

        # Layer 2: Content type validation
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{file.content_type}' is not allowed",
            )

        # Layer 3: Filename validation
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        # Check for dangerous patterns in filename
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, file.filename):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid filename contains dangerous patterns",
                )

        # Read file content for comprehensive analysis
        content = await file.read()
        await file.seek(0)  # Reset file pointer

        # Layer 4: Comprehensive file analysis
        analysis_report = analyze_file_comprehensively(content, file.filename, file.content_type)

        # Apply security level filtering
        if security_level == "strict":
            if analysis_report.validation_result in [
                ValidationResult.SUSPICIOUS,
                ValidationResult.MALICIOUS,
            ]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"File rejected - Security analysis: {', '.join(analysis_report.threats_detected)}",
                )
        elif security_level == "standard":
            if analysis_report.validation_result == ValidationResult.MALICIOUS:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"File rejected - Malicious content detected: {', '.join(analysis_report.threats_detected)}",
                )
        # "basic" level only rejects on fatal errors (already handled above)

        # Layer 5: Legacy validation checks (for backward compatibility)
        if enable_content_validation:
            if not validate_file_content(content, file.content_type, file.filename):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="File content does not match declared type",
                )

        if enable_malware_check:
            if not check_for_malicious_content(content, file.filename):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="File contains potentially dangerous content",
                )

        # Update filename with sanitized version
        file.filename = analysis_report.filename

        # Log validation results
        logger.info(
            f"File validation complete: {analysis_report.filename} "
            f"(Result: {analysis_report.validation_result.value}, "
            f"Score: {analysis_report.security_score:.2f}, "
            f"Time: {analysis_report.validation_time:.3f}s)"
        )

        if analysis_report.threats_detected:
            logger.warning(
                f"Threats detected in {analysis_report.filename}: {analysis_report.threats_detected}"
            )

        return file, analysis_report

    return validator


def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


def get_safe_upload_path(filename: str, upload_dir: str = None) -> Path:
    """Get a safe upload path preventing directory traversal."""
    if upload_dir is None:
        upload_dir = settings.upload_dir

    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Ensure upload directory is absolute
    upload_path = Path(upload_dir).resolve()

    # Construct file path
    file_path = upload_path / safe_filename

    # Verify the resolved path is within upload directory
    if not str(file_path.resolve()).startswith(str(upload_path)):
        raise ValueError("Invalid file path")

    return file_path


def quarantine_file(file_content: bytes, analysis_report: FileAnalysisReport) -> str:
    """Quarantine a suspicious file for manual review."""
    quarantine_dir = Path(settings.upload_dir) / "quarantine"
    quarantine_dir.mkdir(exist_ok=True)

    # Create quarantine filename with timestamp and hash
    timestamp = int(time.time())
    quarantine_filename = f"{timestamp}_{analysis_report.file_hash[:8]}_{analysis_report.filename}"
    quarantine_path = quarantine_dir / quarantine_filename

    # Write file to quarantine
    with open(quarantine_path, "wb") as f:
        f.write(file_content)

    # Write analysis report
    report_path = quarantine_path.with_suffix(".json")
    import json

    with open(report_path, "w") as f:
        json.dump(
            {
                "filename": analysis_report.filename,
                "original_filename": analysis_report.original_filename,
                "content_type": analysis_report.content_type,
                "detected_type": analysis_report.detected_type,
                "file_size": analysis_report.file_size,
                "file_hash": analysis_report.file_hash,
                "validation_result": analysis_report.validation_result.value,
                "security_score": analysis_report.security_score,
                "threats_detected": analysis_report.threats_detected,
                "recommendations": analysis_report.recommendations,
                "validation_time": analysis_report.validation_time,
                "quarantined_at": timestamp,
            },
            indent=2,
        )

    logger.warning(f"File quarantined: {quarantine_filename} - {analysis_report.threats_detected}")
    return str(quarantine_path)


class EnhancedFileValidator:
    """Enhanced file validator with advanced security features."""

    def __init__(
        self,
        max_size: int = None,
        allowed_types: List[str] = None,
        security_level: str = "standard",
        enable_quarantine: bool = True,
    ) -> None:
        self.max_size = max_size or settings.max_file_size
        self.allowed_types = allowed_types or settings.allowed_file_types
        self.security_level = security_level
        self.enable_quarantine = enable_quarantine

        if isinstance(self.allowed_types, str):
            self.allowed_types = [self.allowed_types]

    async def validate_and_analyze(
        self, file: UploadFile
    ) -> Tuple[UploadFile, FileAnalysisReport, Optional[str]]:
        """Validate file with comprehensive analysis and optional quarantine."""
        # Basic validations
        if file.size and file.size > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the limit of {self.max_size / 1024 / 1024} MB",
            )

        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{file.content_type}' is not allowed",
            )

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        # Read content and analyze
        content = await file.read()
        await file.seek(0)

        analysis_report = analyze_file_comprehensively(content, file.filename, file.content_type)
        file.filename = analysis_report.filename

        quarantine_path = None

        # Apply security policies
        if self.security_level == "strict":
            if analysis_report.validation_result in [
                ValidationResult.SUSPICIOUS,
                ValidationResult.MALICIOUS,
            ]:
                if self.enable_quarantine:
                    quarantine_path = quarantine_file(content, analysis_report)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="File rejected - Security risk detected",
                )
        elif self.security_level == "standard":
            if analysis_report.validation_result == ValidationResult.MALICIOUS:
                if self.enable_quarantine:
                    quarantine_path = quarantine_file(content, analysis_report)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="File rejected - Malicious content detected",
                )
            elif (
                analysis_report.validation_result == ValidationResult.SUSPICIOUS
                and self.enable_quarantine
            ):
                quarantine_path = quarantine_file(content, analysis_report)

        return file, analysis_report, quarantine_path
