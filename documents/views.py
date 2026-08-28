from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
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


def document_cache_key(document_id):
    return f"document-workflow:{document_id}"


def get_document_state(document_id):
    return cache.get(document_cache_key(document_id))


class UploadDocumentView(APIView):
    def get(self, request):
        return render(request, "documents/index.html")

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)

        if serializer.is_valid():
            pdf_file = serializer.validated_data["file"]

            try:
                validate_pdf_document(pdf_file)
            except InvalidPDFError as e:
                return Response({
                    "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST)

            try:
                text = extract_text(pdf_file)
            except TextExtractionError as e:
                return Response(
                    {"message": str(e)},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            document_id = str(uuid4())
            cache.set(
                document_cache_key(document_id),
                {"filename": pdf_file.name, "text": text},
                timeout=settings.DOCUMENT_CACHE_TTL,
            )

            return Response({
                "document_id": document_id,
                "filename": pdf_file.name,
                "message": "File uploaded and text extracted",
                "text": text,
            })

        return Response(
            data=serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )


class ClassifyDocumentView(APIView):
    def post(self, request, document_id):
        state = get_document_state(document_id)
        if state is None:
            return Response({"message": "Document not found or expired"}, status=status.HTTP_404_NOT_FOUND)

        try:
            classification = classify_text(state["text"])
        except ClassificationError as e:
            return Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        state["classification"] = classification
        cache.set(document_cache_key(document_id), state, timeout=settings.DOCUMENT_CACHE_TTL)
        return Response({"document_id": document_id, "classification": classification})



class ExtractDocumentFieldsView(APIView):
    def post(self, request, document_id):
        state = get_document_state(document_id)
        if state is None:
            return Response({"message": "Document not found or expired"}, status=status.HTTP_404_NOT_FOUND)
        if "classification" not in state:
            return Response(
                {"message": "Classify the document before extracting fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fields = doc_fields_extraction(
                state["classification"]["doc_type"],
                state["text"],
            )
        except FieldExtractionNotSupportedError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ClassificationError as e:
            return Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        state["fields"] = fields
        cache.set(document_cache_key(document_id), state, timeout=settings.DOCUMENT_CACHE_TTL)
        return Response({"document_id": document_id, "fields": fields})

