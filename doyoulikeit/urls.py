from django.conf.urls import patterns, include, url
from . import views, models
from .models import Thing

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'things/bounce$', views.bounce),
    url(r'^things/(?P<thing_id>\d+)/likes/(?P<user_id>.+)$', views.likes),
    url(r'^things/(?P<thing_id>\d+)$', views.thing_view),
    url(r'^things/(?P<thing_id>[^/]+)$', views.thing_redirect),
)

try:
    Thing.objects.get(id=1)
except Thing.DoesNotExist:
    t = Thing(iri='http://dbpedia.org/resource/Kevin_Bacon')
    t.save()
