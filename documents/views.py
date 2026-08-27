from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DocumentUploadSerializer

class UploadDocumentView(APIView):
    def get(self, request):
        return render(request, "documents/upload.html")

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)

        if serializer.is_valid():
            pdf_file = serializer.validated_data["file"]

            return Response({
                "filename": pdf_file.name,
                "message": "File uploaded successfully"
            })

        return render(
            request,
            "documents/upload.html",
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

