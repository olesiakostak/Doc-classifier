from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DocumentUploadSerializer
from .validators import validate_pdf_document, InvalidPDFError
from classification.extractors import extract_text
from classification.classify import classify_text
from classification.extract_fields import doc_fields_extraction
from classification.exceptions import (
    ClassificationError,
    FieldExtractionNotSupportedError,
    TextExtractionError,
)
from classification.schemas import FIELD_NAMES_BY_TYPE


def extract_text_from_request(request):
    serializer = DocumentUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return None, None, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    pdf_file = serializer.validated_data["file"]
    try:
        validate_pdf_document(pdf_file)
        text = extract_text(pdf_file)
    except InvalidPDFError as e:
        return None, None, Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except TextExtractionError as e:
        return None, None, Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    return pdf_file, text, None


class ClassifyDocumentView(APIView):
    def post(self, request):
        pdf_file, text, error_response = extract_text_from_request(request)
        if error_response:
            return error_response

        try:
            classification = classify_text(text)
        except ClassificationError as e:
            return Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        doc_type = classification["doc_type"]
        return Response({
            "filename": pdf_file.name,
            "classification": classification,
            "field_extraction_supported": doc_type in FIELD_NAMES_BY_TYPE,
            "available_field_types": list(FIELD_NAMES_BY_TYPE),
        })



class ExtractDocumentFieldsView(APIView):
    def post(self, request):
        doc_type = request.data.get("doc_type")
        if not doc_type:
            return Response({"message": "doc_type is required"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_file, text, error_response = extract_text_from_request(request)
        if error_response:
            return error_response

        try:
            fields = doc_fields_extraction(doc_type, text)
        except FieldExtractionNotSupportedError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ClassificationError as e:
            return Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"filename": pdf_file.name, "doc_type": doc_type, "fields": fields})

