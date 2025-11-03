"""Custom exception classes for Docling service."""

from typing import Any, Dict, Optional


class LightRAGCVException(Exception):
    """Base exception for LightRAG-CV project."""

    def __init__(
        self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., "PARSING_FAILED")
            details: Additional error context
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class DocumentParsingError(LightRAGCVException):
    """Raised when document parsing fails."""

    def __init__(
        self,
        message: str = "Document parsing failed",
        error_code: str = "PARSING_FAILED",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)


class FileSizeExceededError(LightRAGCVException):
    """Raised when uploaded file exceeds size limit."""

    def __init__(
        self,
        message: str = "File size exceeds maximum allowed",
        error_code: str = "FILE_TOO_LARGE",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)


class InvalidFileFormatError(LightRAGCVException):
    """Raised when file format is not supported."""

    def __init__(
        self,
        message: str = "Invalid file format",
        error_code: str = "INVALID_FILE_FORMAT",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)
