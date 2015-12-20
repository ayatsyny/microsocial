from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages.views import flatpage
from django.views.generic import TemplateView, RedirectView
#from django.contrib.flatpages.urls import urlpatterns as flatpages_urlpatterns

urlpatterns = [
    url(
        r'^$',
        TemplateView.as_view(template_name='base.html'),
        name='main'
    ),
    url(
        r'^login$',
        TemplateView.as_view(template_name='microsocial/login.html'),
        name='login'
    ),
    url(
        r'^registration$',
        TemplateView.as_view(template_name='microsocial/registration.html'),
        name='registration'
    ),
    url(
        r'^password-recovery',
        TemplateView.as_view(template_name='microsocial/password_recovery_email.html'),
        name='password-recovery'
    ),
    url(
        r'^person',
        include('person.urls')
    ),
    url(
        r'^admin',
        include(admin.site.urls),
    ),
    url(
        r'^logo\.jpg$',
        RedirectView.as_view(url=static('microsocial/img/logo.jpg')),
    ),
    url(
        r'^pages(?P<url>.*)$',
        flatpage,
        name='flatpage'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
