from behave import *
from hamcrest import *
from things.models import Thing

@when(u'I visit the page for "{title}"')
def visit(context, title):
    iri = 'http://dbpedia.org/resource/' + title.replace(' ', '_')
    thing = Thing(iri=iri)
    context.client.visit('/things/' + thing.pk)


@when(u'I visit any page')
def visit_any(context):
    visit(context, 'Kevin Bacon')
