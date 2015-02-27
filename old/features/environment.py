# -*- coding: utf-8 -*-
from rdflib import Namespace
import hyperspace
from laconia import ThingFactory
from things.models import Thing, User, Vote


def page_object(iri, graph):
    graph.bind('schema', Namespace('http://schema.org/'), override=True)
    return ThingFactory(graph)(iri)


def before_all(context):
    Vote.objects.all().delete()
    User.objects.all().delete()
    Thing.objects.all().delete()

    context.page = hyperspace.jump('http://localhost:5100/')

    context.page_object = lambda: page_object(context.iri, context.page.data)

