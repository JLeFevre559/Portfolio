# Resume/urls.py
from django.urls import path, include
from Resume.views import (
    Index,
    ResumeView,
    ClipboardView,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", Index.as_view(), name="Index"),
    path("resume/", ResumeView.as_view(), name="Resume"),
    path("projects/clipboard", ClipboardView.as_view(), name="Clipboard"),
]
