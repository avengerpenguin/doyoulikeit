from hamcrest import *
from behave import *
from rdflib import Graph, URIRef, Literal


@then(u'the page should have the title "{title}"')
def impl(context, title):
    # For humans
    page_h1 = context.soup().findAll('h1')[0]
    assert title == page_h1.text, "Page should contain h1 '%s', has '%s'" % (title, page_h1.text)

    # For robots
    g = Graph()
    g.parse(data=context.soup().html, format='html')
    assert (URIRef('http://dbpedia.org/resource/Kevin_Bacon'), URIRef('http://schema.org/name'), Literal(title, lang='en')) in g


@then(u'the page should have some kind of description of him')
def impl(context):
    # For robots
    g = Graph()
    g.parse(data=context.browser.response().read(), format='html')

    assert (URIRef('http://dbpedia.org/resource/Errol_Brown'), URIRef('http://schema.org/description'), None) in g

@then(u'I should be taken back to my original page')
def impl(context):
    assert context.browser.geturl() == context.page
