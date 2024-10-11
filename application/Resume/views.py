from django.views.generic import TemplateView

class Index(TemplateView):
    template_name = "index.html"

class ResumeView(TemplateView):
    template_name = "resume/resume.html"

class ClipboardView(TemplateView):
    template_name = "projects/clipboard/clipboard.html"