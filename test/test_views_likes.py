import re

import pytest
import responses
import testypie

from doyoulikeit.models import Thing, User, Vote


@pytest.fixture(autouse=True, scope="module")
def mock_responses(request):
    def callback(http_request):
        responses.stop()
        response = testypie.get_response(http_request.url, http_request.headers)
        responses.start()
        return response["code"], response["headers"], response["body"]

    responses.start()
    responses.add_callback(responses.GET, re.compile(".*"), callback=callback)
    request.addfinalizer(responses.stop)


@pytest.mark.django_db
def test_anonymous_has_votes_stored_in_session(client):
    thing = Thing.get_or_create("http://dbpedia.org/resource/Mandelbrot_set")
    thing.save()

    client.post("/things/" + str(thing.pk) + "/likes/0")
    assert len(client.session["vote_stash"]) == 1

    vote = Vote.objects.get(pk=client.session["vote_stash"][0])
    assert vote.thing == thing


@pytest.mark.django_db
def test_anonymous_redirected_after_voting(client):
    thing = Thing.get_or_create("http://dbpedia.org/resource/Peppa_Pig")
    thing.save()
    thing_url = "http://testserver" + thing.get_absolute_url()

    response = client.post("/things/" + str(thing.pk) + "/likes/0")
    assert response.status_code == 302
    assert response["Location"] == thing_url


@pytest.mark.django_db
def test_anonymous_users_cannot_double_vote(client):
    thing = Thing.get_or_create("http://dbpedia.org/resource/Duck")
    thing.save()

    client.post("/things/" + str(thing.pk) + "/likes/0")
    assert len(client.session["vote_stash"]) == 1

    response = client.post("/things/" + str(thing.pk) + "/likes/0")
    assert response.status_code == 409  # Conflict


@pytest.mark.django_db
def test_authenticated_user_can_like_thing(client):
    thing = Thing.get_or_create("http://dbpedia.org/resource/Potato")
    thing.save()

    user = User.objects.create_user(username="peter", password="rainbow87")

    client.login(username="peter", password="rainbow87")
    client.post("/things/" + str(thing.pk) + "/likes/" + str(user.id))

    assert Vote.objects.all().count() == 1
    vote = Vote.objects.all()[0]
    assert vote.user == user
    assert vote.thing == thing


@pytest.mark.django_db
def test_authenticated_user_cannot_vote_against_another_account(client):
    thing = Thing.get_or_create("http://dbpedia.org/resource/Rabbit")
    thing.save()

    edna = User.objects.create_user(username="edna", password="hamster29")
    john = User.objects.create_user(username="john", password="frivolity92")

    client.login(username=edna.username, password="hamster29")
    response = client.post("/things/" + str(thing.pk) + "/likes/" + str(john.id))
    assert response.status_code == 403
    assert Vote.objects.all().count() == 0


@pytest.mark.django_db
def test_authenticated_cannot_double_vote(client):
    thing = Thing.get_or_create("http://dbpedia.org/resource/Potato")
    thing.save()

    user = User.objects.create_user(username="peter", password="rainbow87")
    client.login(username="peter", password="rainbow87")

    client.post("/things/" + str(thing.pk) + "/likes/" + str(user.id))
    assert Vote.objects.all().count() == 1
    response = client.post("/things/" + str(thing.pk) + "/likes/" + str(user.id))
    assert response.status_code == 409  # Conflict
    assert Vote.objects.all().count() == 1


@pytest.mark.django_db
def test_anonymous_has_votes_saved_after_login(client):
    thing = Thing.get_or_create("http://dbpedia.org/resource/Mandelbrot_set")
    thing.save()

    client.post("/things/" + str(thing.pk) + "/likes/0")
    print(list(Vote.objects.all()))
    assert Vote.objects.all().count() == 1
    vote = Vote.objects.all()[0]
    assert vote.thing == thing
    assert vote.user == None

    user = User.objects.create_user(username="peter", password="rainbow87")
    print(
        client.post(
            "/accounts/login/", {"login": user.username, "password": "rainbow87"}
        )
    )
    print(list(Vote.objects.all()))
    assert Vote.objects.all().count() == 1
    vote = Vote.objects.all()[0]
    assert vote.thing == thing
    assert vote.user == user
