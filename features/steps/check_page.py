from hamcrest import *
from behave import then
from rdflib import Graph, URIRef, Literal, Namespace


@then(u'the page should have the title "{title}"')
def impl(context, title):
    print context.page.data.serialize(format='turtle')
    assert_that(list(context.page_object().schema_name), contains(title))


@then(u'the page should have some kind of description of him')
def impl(context):
    assert len(context.page_object().schema_description) > 0

@then(u'I should be taken back to my original page')
def impl(context):
    assert context.browser.geturl() == context.page
