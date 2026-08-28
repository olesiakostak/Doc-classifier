from django.views.generic import TemplateView
from .views import ClassifyDocumentView, ExtractDocumentFieldsView
from django.urls import path

urlpatterns = [
    path("upload/", TemplateView.as_view(template_name="documents/upload.html"), name="document-upload"),
    path("classify/", ClassifyDocumentView.as_view(), name="document-classify"),
    path("extract-fields/", ExtractDocumentFieldsView.as_view(), name="document-extract-fields"),
]

