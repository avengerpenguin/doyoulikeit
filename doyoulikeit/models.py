import laconia
import hyperspace
from rdflib import Graph, URIRef
from django.db import models
from django.contrib.auth.models import User
from django_session_stashable import SessionStashable
from httplib2 import iri2uri
import requests
from cachecontrol import CacheControl


http_client = CacheControl(requests.Session())
http_client.headers['Accept'] = 'text/turtle'


class LaconicModel(models.Model):

    iri = models.CharField(max_length=255, unique=True)

    def __init__(self, *args, **kwargs):
        super(LaconicModel, self).__init__(*args, **kwargs)

        graph = Graph()
        graph.bind('dbpedia', 'http://dbpedia.org/resource/')
        graph.bind('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
        graph.bind('schema', 'http://schema.org/')

        home = hyperspace.jump('http://dyli-thingy.herokuapp.com/',
                               client=http_client)
        thing = home.queries['lookup'][0].build({'iri': self.iri}).submit()
        graph = graph + thing.data

        if len(graph) == 0:
            raise LaconicModel.DoesNotExist('No data found for: ' + self.iri)

        self._graph = graph
        factory = laconia.ThingFactory(graph)
        self._entity = factory(iri2uri(self.iri))

    def __getattr__(self, item):
        vals = set(getattr(self._entity, item))
        vals = map(LaconicModel.entity_to_thing, vals)
        return list(vals)

    @classmethod
    def get_or_create(cls, iri):
        things = cls.objects.filter(iri=iri)
        if things.count() == 0:
            thing = cls(iri=iri)
            thing.save()
        else:
            thing = things[0]

        return thing

    @classmethod
    def entity_to_thing(cls, entity):
        if isinstance(entity, laconia.Thing):
            thing = cls.get_or_create(entity._id)
            thing.set_lang('en')
            return thing
        else:
            return entity

    def set_lang(self, newlang):
        self._entity.lang = newlang


def force_url_value_to_str(entity, attr):
    urls = getattr(entity, attr)
    if len(urls) == 0:
        return None
    else:
        return set(urls).pop()._id


class Thing(LaconicModel):
    """Placeholder for any specific logic for the "Do You Like It?" Thing model.
    Currently empty as it only serves as syntactic sugar for the views to be
    able to talk about distinct models."""
    def get_absolute_url(self):
        return u'/things/' + str(self.id)

    def __str__(self):
        self.set_lang('en')
        names = self.schema_name
        if names:
            return str(names[0])
        else:
            return str(self.iri)

    @property
    def schema_image(self):
        return force_url_value_to_str(self._entity, 'schema_image')

    @property
    def schema_thumbnailUrl(self):
        return force_url_value_to_str(self._entity, 'schema_thumbnailUrl')


class Vote(models.Model, SessionStashable):
    LIKE = 'L'
    DISLIKE = 'D'
    MEH = 'M'

    creator_field = 'user'
    session_variable = 'vote_stash'

    user = models.ForeignKey(User, null=True, blank=True)
    thing = models.ForeignKey(Thing)
    sentiment = models.CharField(max_length=1, choices=(
        (LIKE, 'like'),
        (DISLIKE, 'dislike'),
        (MEH, 'meh'),
    ))

    def __str__(self):
        self.thing.set_lang('en')
        return 'Vote({user} {sentiment}s {thing})'.format(user=self.user, sentiment=self.sentiment, thing=self.thing)
