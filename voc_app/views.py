from django.shortcuts import render
from django.views.generic import TemplateView

class PublishView(TemplateView):
  template_name = "survey/publish.html"
