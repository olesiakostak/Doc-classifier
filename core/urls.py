from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/documents/upload/")),
    path("admin/", admin.site.urls),
    path("documents/", include("documents.urls")),
]

