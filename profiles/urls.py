from django.conf.urls import url

from profiles import views

urlpatterns = [
    url(r'^(?P<user_id>[^/]+)$', views.profile_view),
]
