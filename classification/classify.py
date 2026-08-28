from groq import Groq
from groq import APIConnectionError, RateLimitError, APIStatusError, APIError
from django.conf import settings
from classification.exceptions import ClassificationError
from classification.schemas import document_classification_schema, DOC_TYPES
import json
import math

GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_TEXT_MODEL = "openai/gpt-oss-120b"


def classify_text(text: str) -> dict:
    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = {
                "role": "system",
                "content": (
                    "You are a document classification system for american logistic companies."
                    "You recieve extracted from document text."
                    f"Classify the document into one of the following types: {", ".join(DOC_TYPES)}"
                    "You responce  only with type of document and confidence score."
                    "No comments or explanations."
        ),
    }

    try:
        response = client.chat.completions.create(
            model=GROQ_TEXT_MODEL,
            messages=[
                system_prompt,
                {"role": "user", "content": text},
            ],
            response_format=document_classification_schema,
            temperature=0,
        )
    except APIConnectionError as e:
        raise ClassificationError(f"Could not reach Groq API: {e}")
    except RateLimitError as e:
        raise ClassificationError(f"Groq API rate limit exceeded: {e}")
    except APIStatusError as e:
        raise ClassificationError(f"Groq API returned an error status: {e}")
    except APIError as e:
        raise ClassificationError(f"Groq API error: {e}")


    try:
        result = json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, IndexError, AttributeError) as e:
        raise ClassificationError(f"Failed to parse model response as JSON: {e}")


    try:
        doc_type = result["doc_type"]
        confidence = result["confidence"]
    except (KeyError, TypeError) as e:
        raise ClassificationError(f"Model response missing expected field: {e}") from e

    if doc_type not in DOC_TYPES:
        raise ClassificationError("Model response contains an invalid document type")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise ClassificationError("Model response contains an invalid confidence score")
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ClassificationError("Confidence score must be between 0 and 1")


    return {
        "doc_type": doc_type,
        "confidence": confidence,
    }
    