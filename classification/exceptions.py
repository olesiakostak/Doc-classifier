class LLMServiceError(Exception):
    """Base exception for failures when calling the LLM service."""
    pass


class TextExtractionError(LLMServiceError):
    """Raised when text extraction from a scanned PDF page fails."""
    pass


class ClassificationError(LLMServiceError):
    """Raised when document classification fails for any reason."""
    pass