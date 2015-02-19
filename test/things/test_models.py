import re
import pytest
import testypie
import responses
from rdflib import Graph, URIRef, Literal, RDFS
from things.models import LaconicModel




@pytest.fixture(autouse=True, scope='session')
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


# @pytest.mark.django_db
# def test_creating_laconic_model_from_existing_graph():
#     iri = 'http://dbpedia.org/resource/Kevin_Bacon'
#     graph = Graph()
#     graph.parse(iri)
#
#     extra_prop = 'http://example.com/my/extra/property'
#     message = 'This proves the existing graph was used.'
#     marker = (URIRef(iri),
#               URIRef(extra_prop),
#               Literal(message))
#     graph.add(marker)
#
#     lm = LaconicModel(iri=iri, graph=graph)
#     assert message in getattr(lm, extra_prop)

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
