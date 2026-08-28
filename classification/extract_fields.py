from groq import Groq
from groq import APIConnectionError, RateLimitError, APIStatusError, APIError
from django.conf import settings
from classification.exceptions import ClassificationError
from classification.schemas import extraction_field_schema, FIELD_NAMES_BY_TYPE
import json


GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_TEXT_MODEL = "openai/gpt-oss-120b"


def doc_fields_extraction(doc_type: str, text: str) -> dict:
    client = Groq(api_key=GROQ_API_KEY)

    field_names = FIELD_NAMES_BY_TYPE[doc_type]
    fields_list = ", ".join(field_names)

    system_prompt = {
        "role": "system",
        "content": (
            "You are a document fields extraction system for american logistic companies. "
            f"You receive text extracted from a {doc_type} document. "
            f"Extract the following fields: {fields_list}. "
            "For each field, return its value and your confidence score. "
            "If a field is not present in the text, return null for its value. "
            "Respond only with the extracted fields and their confidence scores. "
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
            response_format=extraction_field_schema[doc_type],
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

    return result
    