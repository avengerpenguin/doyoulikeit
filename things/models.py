import laconia
from rdflib import Graph, URIRef, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from django.db import models
from django.contrib.auth.models import User


#store = SPARQLStore("http://dbpedia.org/sparql", context_aware=False)

#graph = Graph(store)
graph = Graph()

graph.bind("dbpedia", "http://dbpedia.org/resource/")
graph.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")

DBPEDIA = Namespace('http://dbpedia.org/resource/')

factory = laconia.ThingFactory(graph)


class LaconicModel(object):
    """
    A layer over Laconia that gives (a subset of) the API one would expect from
    a Django model.
    """

    @classmethod
    def get(cls, pk=None):
        """
        Allows fetching a single instance of a model by its ID/primary key
        as a Django model would allow. Here, however, the ID is in the
        form namespace_ident, e.g. dbpedia_Kevin_Bacon. This is currently just
        a wrapper around the constructor as there is no distinction between
        creating a new object and creating a model for an existing entity.
        """
        return cls(pk)

    def __init__(self, ident):
        """
        Takes an ident in the form namespace_ident, e.g. dbpedia_Kevin_Bacon,
        and creates a model instance representing the respective entity. This
        is done by creating not only a laconia "thing" instance (that this
        class or a subclass then wraps), but pre-populates the global graph
        with whatever information can be found by dereferencing the full URI.
        """
        self._ident = ident
        self._entity = factory(ident)
        graph.parse(self._entity._id)

    @property
    def pk(self):
        """
        Returns the URI of the entity this model represents. This can be used
        in "itemid" properties in HTML microdata, for example.
        """
        return self._entity._id

    @property
    def ident(self):
        return self._ident

    def __getattr__(self, item):
        """
        The wrapped entity will likely return a ResourceSet of many matches
        for a simple attribute lookup. This is due to the multilingual nature
        of the RDF model, especially on DBPedia. This wrapper allows the full
        expressivity of being able to fetch any predicate as an object property,
        but ensures we get exactly one match each time in the desired language.
        """
        return [value for value in getattr(self._entity, item) if value.language == 'en'][0]


class Thing(LaconicModel):
    """Placeholder for any specific logic for the "Do You Like It?" Thing model.
    Currently empty as it only serves as syntactic sugar for the views to be
    able to talk about distinct models."""
    def get_absolute_url(self):
        return '/things/' + self.ident.split('_', 1)[1]

    def __unicode__(self):
        return self.rdfs_label

    def __str__(self):
        return unicode(self)


class LaconicField(models.CharField):
    description = "A link to an RDF model class."
    __metaclass__ = models.SubfieldBase

    def __init__(self, model_class, *args, **kwargs):
        self.model_class = model_class
        kwargs['max_length'] = 200
        super(LaconicField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return value.ident

    def to_python(self, value):
        if isinstance(value, self.model_class):
            return value
        return self.model_class(value)


class Vote(models.Model):
    LIKE = 'L'
    DISLIKE = 'D'
    MEH = 'M'

    class Meta:
        unique_together = (("user", "thing", "sentiment"),)
    user = models.ForeignKey(User)
    thing = LaconicField(Thing)
    sentiment = models.CharField(max_length=1, choices=(
        (LIKE, 'like'),
        (DISLIKE, 'dislike'),
        (MEH, 'meh'),
    ))
