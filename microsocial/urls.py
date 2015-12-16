from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'microsocial.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
