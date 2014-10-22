# -*- coding: utf-8 -*-
from rdflib import Namespace
import hyperspace
from laconia import ThingFactory


def page_object(iri, graph):
    graph.bind('schema', Namespace('http://schema.org/'), override=True)
    return ThingFactory(graph)(iri)


def before_all(context):
    context.page = hyperspace.jump('http://localhost:5000/')

    context.page_object = lambda: page_object(context.iri, context.page.data)
