from behave import *
import hyperspace
from things.models import Thing

@when(u'I visit the page for "{title}"')
def visit(context, title):
    iri = 'http://dbpedia.org/resource/' + title.replace(' ', '_')
    try:
        thing = Thing.objects.get(iri=iri)
    except Thing.DoesNotExist, e:
        thing = Thing(iri=iri)
        thing.save()

    context.iri = iri
    context.page = hyperspace.jump(
        'http://localhost:5000/things/{}'.format(thing.id))
    print context.page.data.serialize(format='turtle')


@when(u'I visit any page')
def visit_any(context):
    visit(context, 'Kevin Bacon')
