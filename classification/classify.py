from groq import Groq
from groq import APIConnectionError, RateLimitError, APIStatusError, APIError
from django.conf import settings
from classification.exceptions import ClassificationError
import json

GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_TEXT_MODEL = "openai/gpt-oss-120b"


def classify_text(text: str) -> dict:
    client = Groq(api_key=GROQ_API_KEY)

    response_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "document_classification",
            "schema": {
                "type": "object",
                "properties": {
                    "doc_type": {
                        "type": "string",
                        "enum": ["Invoice", "BOL", "POD", "Rate Confirmation", "Packing List", "Other"],
                    },
                    "confidence": {
                        "type": "number",
                    },
                },
                "required": ["doc_type", "confidence"],
                "additionalProperties": False,
            },
        },
    }

    system_prompt = {
                "role": "system",
                "content": (
                    "You are a document classification system for american logistic companies."
                    "You recieve extracted from document text."
                    "Classify the document into one of the following types: Invoice, BOL, POD, Rate Confirmation, Packing List, Other."
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
            response_format=response_schema,
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
    except KeyError as e:
        raise ClassificationError(f"Model response missing expected field: {e}")


    return {
        "doc_type": doc_type,
        "confidence": confidence,
    }
    