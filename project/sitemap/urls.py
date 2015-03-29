from django.conf.urls import patterns, url

from project.sitemap import views


urlpatterns = patterns('',
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^status/(?P<result_key>([a-f\d]{32}))/$', views.Status.as_view(), name='status'),
    url(r'^result/(?P<result_key>([a-f\d]{32}))/$', views.Result.as_view(), name='result'),
)
