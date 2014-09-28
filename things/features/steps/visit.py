from behave import *
from hamcrest import *
from things.models import Thing

@when(u'I visit the page for "{title}"')
def visit(context, title):
    iri = 'http://dbpedia.org/resource/' + title.replace(' ', '_')
    try:
        thing = Thing.objects.get(iri=iri)
    except Thing.DoesNotExist, e:
        thing = Thing(iri=iri)
        thing.save()

    br = context.browser
    context.page = context.url(thing.get_absolute_url())
    br.open(context.page)


@when(u'I visit any page')
def visit_any(context):
    visit(context, 'Kevin Bacon')
