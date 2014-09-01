from behave import *


@when(u'I visit the page for Kevin Bacon')
def step_impl(context):
    br = context.browser
    br.visit('/things/Kevin_Bacon')
    context.current_item = 'http://dbpedia.org/resource/Kevin_Bacon'


@when(u'I visit the page for Errol Brown')
def impl(context):
    br = context.browser
    br.visit('/things/Errol_Brown')


@when(u'I visit the page for "{title}')
def impl(context, title):
    print '/things/' + title
    context.browser.visit('/things/' + title)
