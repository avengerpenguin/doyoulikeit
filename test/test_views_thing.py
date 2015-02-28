import re
import pytest
import responses
import testypie
from doyoulikeit.models import Thing, User


@pytest.fixture(autouse=True, scope='module')
def mock_responses(request):
    def callback(http_request):
        responses.stop()
        response = testypie.get_response(http_request.url, http_request.headers)
        responses.start()
        return response['code'], response['headers'], response['body']

    responses.start()
    responses.add_callback(responses.GET,
                           re.compile('.*'),
                           callback=callback)
    request.addfinalizer(responses.stop)


@pytest.mark.django_db
def test_thing_page_has_title(client):
    thing = Thing.get_or_create('http://dbpedia.org/resource/Kevin_Bacon')
    thing.save()

    response = client.get('/things/' + str(thing.pk))
    assert response.status_code == 200
    assert 'Kevin Bacon' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_thing_page_has_description(client):
    thing = Thing.get_or_create('http://dbpedia.org/resource/Kevin_Bacon')
    thing.save()

    response = client.get('/things/' + str(thing.pk))
    assert response.status_code == 200
    assert 'Kevin Norwood Bacon' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_thing_view_sends_thing_to_context(client):
    thing = Thing.get_or_create('http://dbpedia.org/resource/Kevin_Bacon')
    thing.save()

    response = client.get('/things/' + str(thing.pk))

    assert 'thing' in response.context
    assert response.context['thing'] == thing


@pytest.mark.django_db
def test_thing_view_sends_user_id_zero_when_user_is_anonymous(client):
    thing = Thing.get_or_create('http://dbpedia.org/resource/Kevin_Bacon')
    thing.save()

    response = client.get('/things/' + str(thing.pk))
    print(response.context)
    assert 'thing' in response.context
    assert response.context['user_id'] == 0


@pytest.mark.django_db
def test_thing_view_sends_user_id_when_user_is_logged_in(client):
    thing = Thing.get_or_create('http://dbpedia.org/resource/Kevin_Bacon')
    thing.save()

    user = User.objects.create_user(username='peter', password='rainbow87')

    client.login(username='peter', password='rainbow87')
    response = client.get('/things/' + str(thing.pk))

    assert 'thing' in response.context
    assert response.context['user_id'] == user.id
