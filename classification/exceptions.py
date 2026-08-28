class LLMServiceError(Exception):
    """Base exception for failures when calling the LLM service."""
    pass


class TextExtractionError(LLMServiceError):
    """Raised when text extraction from a scanned PDF page fails."""
    pass


class ClassificationError(LLMServiceError):
    """Raised when document classification fails for any reason."""
    pass

class FieldExtractionNotSupportedError(LLMServiceError):
    """
    Raised when field extraction is requested for a document type
    that has no defined field schema (e.g. "Other")."""
    pass