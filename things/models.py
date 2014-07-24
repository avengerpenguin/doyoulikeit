import laconia
from rdflib import Graph, URIRef, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLStore

store = SPARQLStore("http://dbpedia.org/sparql", context_aware=False)

graph = Graph(store)


graph.bind("dbpedia", "http://dbpedia.org/resource/")
graph.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")

DBPEDIA = Namespace('http://dbpedia.org/resource/')

factory = laconia.ThingFactory(graph)

class Thing(object):
    @staticmethod
    def get(pk=None):
        _ = graph.predicate_objects(DBPEDIA['Kevin_Bacon'])
        return Thing(pk)

    def __init__(self, thing_id):
        self._entity = factory('dbpedia_' + thing_id)

    @property
    def title(self):
        return [label for label in self._entity.rdfs_label if label.language == 'en'][0]
