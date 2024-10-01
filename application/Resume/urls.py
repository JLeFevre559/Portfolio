# Resume/urls.py
from django.urls import path, include
from Resume.views import (
    Index,
    ResumeView,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", Index.as_view(), name="Index"),
    path("resume/", ResumeView.as_view(), name="Resume"),
]
