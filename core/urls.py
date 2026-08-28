from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/documents/upload/")),
    path("documents/", include("documents.urls")),
]

