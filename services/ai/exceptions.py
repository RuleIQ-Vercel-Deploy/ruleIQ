"""
AI-specific exceptions for better error handling and debugging.
"""

from typing import Optional, Dict, Any
from core.exceptions import IntegrationException, BusinessLogicException


class AIServiceException(IntegrationException):
    """Base exception for AI service errors."""
    
    def __init__(
        self, 
        message: str, 
        service_name: str = "AI Service",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.service_name = service_name
        self.error_code = error_code
        self.context = context or {}


class AITimeoutException(AIServiceException):
    """Raised when AI service requests timeout."""
    
    def __init__(
        self, 
        timeout_seconds: float,
        service_name: str = "AI Service",
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"{service_name} request timed out after {timeout_seconds} seconds"
        super().__init__(
            message=message,
            service_name=service_name,
            error_code="AI_TIMEOUT",
            context=context
        )
        self.timeout_seconds = timeout_seconds


class AIQuotaExceededException(AIServiceException):
    """Raised when AI service quota is exceeded."""
    
    def __init__(
        self,
        quota_type: str = "requests",
        service_name: str = "AI Service",
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"{service_name} {quota_type} quota exceeded"
        super().__init__(
            message=message,
            service_name=service_name,
            error_code="AI_QUOTA_EXCEEDED",
            context=context
        )
        self.quota_type = quota_type


class AIModelException(AIServiceException):
    """Raised when AI model encounters an error."""
    
    def __init__(
        self,
        model_name: str,
        model_error: str,
        service_name: str = "AI Service",
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"{service_name} model '{model_name}' error: {model_error}"
        super().__init__(
            message=message,
            service_name=service_name,
            error_code="AI_MODEL_ERROR",
            context=context
        )
        self.model_name = model_name
        self.model_error = model_error


class AIContentFilterException(AIServiceException):
    """Raised when AI content is filtered for safety."""
    
    def __init__(
        self,
        filter_reason: str,
        service_name: str = "AI Service",
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"{service_name} content filtered: {filter_reason}"
        super().__init__(
            message=message,
            service_name=service_name,
            error_code="AI_CONTENT_FILTERED",
            context=context
        )
        self.filter_reason = filter_reason


class AIParsingException(BusinessLogicException):
    """Raised when AI response cannot be parsed."""
    
    def __init__(
        self,
        response_text: str,
        expected_format: str,
        parsing_error: str,
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"Failed to parse AI response as {expected_format}: {parsing_error}"
        super().__init__(message)
        self.response_text = response_text
        self.expected_format = expected_format
        self.parsing_error = parsing_error
        self.context = context or {}


class AIValidationException(BusinessLogicException):
    """Raised when AI response fails validation."""
    
    def __init__(
        self,
        validation_errors: list,
        response_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"AI response validation failed: {', '.join(validation_errors)}"
        super().__init__(message)
        self.validation_errors = validation_errors
        self.response_data = response_data
        self.context = context or {}


# Exception mapping for Google Gemini specific errors
GEMINI_ERROR_MAPPING = {
    "DEADLINE_EXCEEDED": AITimeoutException,
    "RESOURCE_EXHAUSTED": AIQuotaExceededException,
    "INVALID_ARGUMENT": AIModelException,
    "PERMISSION_DENIED": AIServiceException,
    "UNAUTHENTICATED": AIServiceException,
    "UNAVAILABLE": AIServiceException,
    "INTERNAL": AIServiceException,
}


def map_gemini_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> AIServiceException:
    """Map Google Gemini errors to our AI exceptions."""
    error_message = str(error)
    error_type = getattr(error, 'code', None)
    
    # Map by error code if available
    if error_type and error_type.name in GEMINI_ERROR_MAPPING:
        exception_class = GEMINI_ERROR_MAPPING[error_type.name]
        
        if exception_class == AITimeoutException:
            return AITimeoutException(
                timeout_seconds=30.0,  # Default timeout
                service_name="Google Gemini",
                context=context
            )
        elif exception_class == AIQuotaExceededException:
            return AIQuotaExceededException(
                quota_type="API requests",
                service_name="Google Gemini",
                context=context
            )
        else:
            return exception_class(
                message=error_message,
                service_name="Google Gemini",
                error_code=error_type.name,
                context=context
            )
    
    # Map by error message patterns
    if "timeout" in error_message.lower():
        return AITimeoutException(
            timeout_seconds=30.0,
            service_name="Google Gemini",
            context=context
        )
    elif "quota" in error_message.lower() or "limit" in error_message.lower():
        return AIQuotaExceededException(
            quota_type="API requests",
            service_name="Google Gemini",
            context=context
        )
    elif "safety" in error_message.lower() or "filter" in error_message.lower():
        return AIContentFilterException(
            filter_reason=error_message,
            service_name="Google Gemini",
            context=context
        )
    
    # Default to generic AI service exception
    return AIServiceException(
        message=error_message,
        service_name="Google Gemini",
        error_code="UNKNOWN_ERROR",
        context=context
    )


def handle_ai_error(
    error: Exception,
    operation: str,
    context: Optional[Dict[str, Any]] = None,
    fallback_response: Optional[Any] = None
) -> tuple[Optional[Any], AIServiceException]:
    """
    Handle AI errors with proper logging and fallback.
    
    Returns:
        Tuple of (fallback_response, mapped_exception)
    """
    from config.logging_config import get_logger
    
    logger = get_logger(__name__)
    
    # Map to our exception types
    if isinstance(error, AIServiceException):
        ai_exception = error
    else:
        ai_exception = map_gemini_error(error, context)
    
    # Log the error with context
    logger.error(
        f"AI error in {operation}: {ai_exception.message}",
        extra={
            "operation": operation,
            "error_code": ai_exception.error_code,
            "service_name": ai_exception.service_name,
            "context": ai_exception.context
        }
    )
    
    return fallback_response, ai_exception
