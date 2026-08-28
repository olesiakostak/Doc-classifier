from .views import UploadDocumentView, ClassifyDocumentView, ExtractDocumentFieldsView
from django.urls import path

urlpatterns = [
    path("upload/", UploadDocumentView.as_view(), name="document-upload"),
    path("<uuid:document_id>/classify/", ClassifyDocumentView.as_view(), name="document-classify"),
    path("<uuid:document_id>/extract-fields/", ExtractDocumentFieldsView.as_view(), name="document-extract-fields"),
]

