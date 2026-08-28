import fitz
import base64
import re
from groq import Groq
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from classification.exceptions import TextExtractionError
from groq import APIConnectionError, RateLimitError, APIStatusError, APIError


GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_VISION_MODEL = "qwen/qwen3.6-27b"
MAX_IMAGES = 1


def strip_thinking_block(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def is_scanned_pdf(pdf: fitz.Document, min_total_chars: int = 5):
    num_of_chars = 0

    for page_num in range(pdf.page_count):
        page = pdf.load_page(page_num)
        text = page.get_text()

        num_of_chars += len(text.strip()) 

    if num_of_chars <= min_total_chars:
        return True

    return False


def extract_text_from_scanned_pdf(pdf: fitz.Document) -> str:
    num_pages = min(pdf.page_count, MAX_IMAGES)

    client = Groq(api_key=GROQ_API_KEY)

    content = []

    for page_num in range(num_pages):
        page = pdf.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  
        img_base64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")

        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img_base64}"},
        })

    system_prompt = {
            "role": "system",
            "content": (
                "Extract all readable text from the provided document pages, "
                "in reading order. Return only the extracted text, "
                "no comments or explanations."
        ),
    }

    try:
        response = client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=[
                system_prompt,
                {"role": "user", "content": content},
            ],
        )
    except APIConnectionError as e:
        raise TextExtractionError(f"Could not reach Groq API: {e}")
    except RateLimitError as e:
        raise TextExtractionError(f"Groq API rate limit exceeded: {e}")
    except APIStatusError as e:
        raise TextExtractionError(f"Groq API returned an error status: {e}")
    except APIError as e:
        raise TextExtractionError(f"Groq API error: {e}")
    
    return strip_thinking_block(response.choices[0].message.content)


def extract_text(pdf: UploadedFile) -> str:
    pdf.seek(0)
    pdf = fitz.open(stream=pdf.read(), filetype="pdf")

    if is_scanned_pdf(pdf):
        return extract_text_from_scanned_pdf(pdf)

    text_from_pages = []
    for page_num in range(pdf.page_count):
        page = pdf.load_page(page_num)
        text_from_pages.append(page.get_text())

    return "\n".join(text_from_pages)


