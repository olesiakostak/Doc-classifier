from django.core.files.uploadedfile import UploadedFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from django.conf import settings
MAX_PDF_SIZE_MB = settings.MAX_PDF_SIZE_MB


class InvalidPDFError(ValueError):
    """Base exception for all PDF validation failures."""
    pass


class FileTooLargeError(InvalidPDFError):
    """Raised when the uploaded file exceeds the maximum allowed size."""
    pass


class CorruptedPDFError(InvalidPDFError):
    """Raised when the file cannot be parsed as a valid PDF."""
    pass


def validate_pdf_document(pdf: UploadedFile):
    """
    Validates that the uploaded file is within size limits and is a
    readable PDF. Returns the number of pages on success.
    """
    size_of_file_mb = float(pdf.size) / 1048576 

    if size_of_file_mb > MAX_PDF_SIZE_MB:
        raise FileTooLargeError(f"File size is too large. Max allowed size: {MAX_PDF_SIZE_MB}")

    pdf.seek(0)
    try:
        reader = PdfReader(pdf.read())
    except PdfReadError:
        raise CorruptedPDFError(f"Failed openning file")   

    page_count = len(reader.pages)
    pdf.seek(0)

    return page_count
    