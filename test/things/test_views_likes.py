import re
import pytest
import responses
import testypie
from things.models import Thing, User, Vote


@pytest.mark.django_db
def test_anonymous_has_votes_stored_in_session(client):
    thing = Thing.get_or_create('http://dbpedia.org/resource/Mandelbrot_set')
    thing.save()

    client.post('/things/' + str(thing.pk) + '/likes/0')
    assert len(client.session['vote_stash']) == 1

    vote = Vote.objects.get(pk=client.session['vote_stash'][0])
    assert vote.thing == thing


@pytest.mark.django_db
def test_anonymous_redirected_after_voting(client):
    thing = Thing.get_or_create('http://dbpedia.org/resource/Mandelbrot_set')
    thing.save()

    response = client.post('/things/' + str(thing.pk) + '/likes/0')
    assert response.status_code == 302
    assert response['Location'] == 'http://testserver' + thing.get_absolute_url()
