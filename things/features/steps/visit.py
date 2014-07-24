from behave import *


@when(u'I visit the page for Kevin Bacon')
def step_impl(context):
    br = context.browser
    br.visit('/things/Kevin_Bacon')
