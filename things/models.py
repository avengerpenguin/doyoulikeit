import laconia
import hyperspace
from rdflib import Graph
from django.db import models
from django.contrib.auth.models import User


class LaconicModel(models.Model):

    iri = models.CharField(max_length=255)

    def __init__(self, iri=None, **kwargs):
        super(LaconicModel, self).__init__(iri=iri, **kwargs)
        graph = Graph()
        graph.bind("dbpedia", "http://dbpedia.org/resource/")
        graph.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")

        home = hyperspace.jump('http://localhost:5000/')
        thing = home.queries['lookup'][0].build({'iri': iri}).submit()
        graph = graph + thing.data

        self._graph = graph
        factory = laconia.ThingFactory(graph)
        self._entity = factory(iri)

    def __getattr__(self, item):
        if item == 'pk':
            return self.pk
        elif item == 'iri':
            return self.iri
        else:
            return [value for value in getattr(self._entity, item)
                    if not value.language or value.language == 'en'][0]


class Thing(LaconicModel):
    """Placeholder for any specific logic for the "Do You Like It?" Thing model.
    Currently empty as it only serves as syntactic sugar for the views to be
    able to talk about distinct models."""
    def get_absolute_url(self):
        return '/things/' + self.ident.split('_', 1)[1]

    def __unicode__(self):
        return self.rdfs_label

    def __str__(self):
        return self.rdfs_label.encode('utf-8')


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


class Vote(models.Model):
    LIKE = 'L'
    DISLIKE = 'D'
    MEH = 'M'

    class Meta:
        unique_together = (("user", "thing", "sentiment"),)
    user = models.ForeignKey(User)
    thing = models.ForeignKey(Thing)
    sentiment = models.CharField(max_length=1, choices=(
        (LIKE, 'like'),
        (DISLIKE, 'dislike'),
        (MEH, 'meh'),
    ))
