from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    url(
        r'^$',
        TemplateView.as_view(template_name='base.html'),
        name='main'
    ),
    url(
        r'^admin',
        include(admin.site.urls),
    ),
    url(
        r'^logo\.jpg$',
        RedirectView.as_view(url=static('microsocial/img/logo.jpg')),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
