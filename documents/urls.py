from .views import UploadDocumentView
from django.urls import path

urlpatterns = [
    path("upload/", UploadDocumentView.as_view(), name="document-upload"),
]

