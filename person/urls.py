# coding=utf-8
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = [
    url(
        r'^profile$',
        TemplateView.as_view(template_name=''),
        name='profile'
    ),
]
