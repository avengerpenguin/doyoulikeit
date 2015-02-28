import re
import pytest
import testypie
import responses
from doyoulikeit.models import LaconicModel


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
def test_creating_laconic_model_from_scratch():
    lm = LaconicModel(iri='http://dbpedia.org/resource/Kevin_Bacon')
    lm.save()
    assert lm is not None


@pytest.mark.django_db
def test_accessing_rdf_attribute():
    lm = LaconicModel(iri='http://dbpedia.org/resource/Kevin_Bacon')
    lm.save()
    assert 'Kevin Bacon' in lm.schema_name


@pytest.mark.django_db
def test_filtering_to_single_language():
    lm = LaconicModel(iri='http://dbpedia.org/resource/Castle')
    lm.save()
    lm.set_lang('en')
    assert set(lm.schema_name) == {'Castle'}
    lm.set_lang('de')
    assert set(lm.schema_name) == {'Burg'}


@pytest.mark.django_db
def test_laconic_model_has_int_id_like_normal_django_model():
    lm = LaconicModel(iri='http://dbpedia.org/resource/Bananaman')
    lm.save()
    assert lm.id == 1


@pytest.mark.django_db
def test_accessing_iri_attribute():
    lm = LaconicModel(iri='http://dbpedia.org/resource/Unicorn')
    lm.save()
    assert lm.iri == 'http://dbpedia.org/resource/Unicorn'


@pytest.mark.django_db
def test_get_or_create_creates_new_instance():
    lm = LaconicModel.get_or_create('http://dbpedia.org/resource/Paddy')
    assert lm.iri == 'http://dbpedia.org/resource/Paddy'
    assert lm.id == 1
    assert 'Paddy' in lm.schema_name


@pytest.mark.django_db
def test_get_or_create_loads_existing_instance():
    lm = LaconicModel(iri='http://dbpedia.org/resource/Bananaman')
    lm.save()
    lm2 = LaconicModel.get_or_create('http://dbpedia.org/resource/Bananaman')
    assert lm2.id == lm.id


@pytest.mark.django_db
def test_linked_entities_are_also_laconic_models():
    lm = LaconicModel(iri='http://dbpedia.org/resource/Brian_Blessed')
    lm.save()
    for film in lm.schema_actor_of:
        assert isinstance(film, LaconicModel)

