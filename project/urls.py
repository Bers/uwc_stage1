from django.conf.urls import patterns, include, url
from django.conf import settings


urlpatterns = patterns('',
    url(r'^', include('project.sitemap.urls')),
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
