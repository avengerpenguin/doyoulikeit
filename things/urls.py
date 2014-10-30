from django.conf.urls import url

from things import views
from things.models import Thing

urlpatterns = [
    url(r'bounce$', views.bounce),
    url(r'^(?P<thing_id>\d+)/likes/(?P<user_id>.+)$', views.likes),
    url(r'^(?P<thing_id>\d+)$', views.thing_view),
    url(r'^(?P<thing_id>[^/]+)$', views.thing_redirect),
]

try:
    Thing.objects.get(id=1)
except Thing.DoesNotExist:
    t = Thing(iri='http://dbpedia.org/resource/Kevin_Bacon')
    t.save()
