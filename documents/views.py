from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DocumentUploadSerializer
from .validators import validate_pdf_document, InvalidPDFError
from classification.extractors import extract_text
from classification.classify import classify_text
from classification.exceptions import ClassificationError, TextExtractionError


class UploadDocumentView(APIView):
    def get(self, request):
        return render(request, "documents/upload.html")

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
                classified_text = classify_text(text)
            except (TextExtractionError, ClassificationError) as e:
                return Response(
                    {"message": str(e)},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            return Response({
                "filename": pdf_file.name,
                "message": classified_text
            })

        return Response(
            data=serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

