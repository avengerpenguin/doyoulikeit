from django.conf.urls import url

from things import views

urlpatterns = [
    url(r'^(?P<thing_id>.+)$', views.thing_view),
]