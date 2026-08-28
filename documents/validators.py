from django.core.files.uploadedfile import UploadedFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from django.conf import settings
MAX_PDF_SIZE_MB = settings.MAX_PDF_SIZE_MB
MAX_PDF_PAGES = settings.MAX_PDF_PAGES


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
    size_of_file_mb = float(pdf.size) / 1048576

    if size_of_file_mb > MAX_PDF_SIZE_MB:
        raise FileTooLargeError(f"File size is too large. Max allowed size: {MAX_PDF_SIZE_MB}")

    pdf.seek(0)
    try:
        reader = PdfReader(pdf)
        page_count = len(reader.pages)
    except (PdfReadError, OSError, ValueError) as exc:
        raise CorruptedPDFError("Failed to open PDF file") from exc

    if page_count == 0:
        raise CorruptedPDFError("PDF file has no pages")
    if page_count > MAX_PDF_PAGES:
        raise InvalidPDFError(f"PDF has too many pages. Max allowed: {MAX_PDF_PAGES}")

    pdf.seek(0)

    return page_count
    