from behave import *
from hamcrest import *


@when(u'I visit the page for Kevin Bacon')
def step_impl(context):
    br = context.browser
    br.visit('/things/Kevin_Bacon')
    context.current_item = 'http://dbpedia.org/resource/Kevin_Bacon'
    assert_that(context.browser.status_code, equal_to(200))


@when(u'I visit the page for Errol Brown')
def impl(context):
    br = context.browser
    br.visit('/things/Errol_Brown')
    assert_that(context.browser.status_code, equal_to(200))


@when(u'I visit the page for "{title}"')
def impl(context, title):
    context.browser.visit('/things/' + title.replace(' ', '_'))
    assert_that(context.browser.status_code, equal_to(200))

