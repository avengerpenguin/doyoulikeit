from __builtin__ import isinstance
import laconia
import hyperspace
from rdflib import Graph, URIRef
from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django_session_stashable import SessionStashable
from httplib2 import iri2uri


class LaconicModel(models.Model):

    iri = models.CharField(max_length=255, unique=True)

    def __init__(self, *args, **kwargs):
        super(LaconicModel, self).__init__(*args, **kwargs)

        graph = Graph()
        graph.bind("dbpedia", "http://dbpedia.org/resource/")
        graph.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        graph.bind("schema", "http://schema.org/")

        hyperspace.session.headers['Accept'] = 'text/turtle'
        home = hyperspace.jump('http://dyli-thingy.herokuapp.com/')
        thing = home.queries['lookup'][0].build({'iri': self.iri}).submit()
        graph = graph + thing.data

        self._graph = graph
        factory = laconia.ThingFactory(graph)
        self._entity = factory(iri2uri(self.iri))

    def __getattr__(self, item):
        if item == 'id':
            return self.id
        elif item == 'iri':
            return self.iri
        else:
            vals = set(getattr(self._entity, item))
            vals = map(convert_entities_to_things, vals)
            return vals

    def set_lang(self, newlang):
        self._entity.lang = newlang


def convert_entities_to_things(entity):
    if isinstance(entity, laconia.Thing):
        thing = Thing.get_or_create(entity._id)
        thing.set_lang('en')
        return thing
    else:
        return entity


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

    def __unicode__(self):
        self.set_lang('en')
        names = self.schema_name
        if names:
            return names[0]
        else:
            return self.iri

    def __str__(self):
        return unicode(self).encode('utf-8')

    @property
    def schema_image(self):
        return force_url_value_to_str(self._entity, 'schema_image')

    @property
    def schema_thumbnailUrl(self):
        return force_url_value_to_str(self._entity, 'schema_thumbnailUrl')

    @classmethod
    def get_or_create(cls, iri):
        things = cls.objects.filter(iri=iri)
        if things.count() == 0:
            thing = cls(iri=iri)
            thing.save()
        else:
            thing = things[0]

        return thing



# class LaconicField(models.CharField):
#     description = "A link to an RDF model class."
#     __metaclass__ = models.SubfieldBase
#
#     def __init__(self, model_class, *args, **kwargs):
#         self.model_class = model_class
#         kwargs['max_length'] = 200
#         super(LaconicField, self).__init__(*args, **kwargs)
#
#     def get_prep_value(self, value):
#         return value.ident
#
#     def to_python(self, value):
#         if isinstance(value, self.model_class):
#             return value
#         return self.model_class(value)


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
