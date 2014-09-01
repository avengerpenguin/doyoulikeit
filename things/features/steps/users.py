from behave import *


@given(u'I am a new visitor')
def impl(context):
    context.browser.cookies.delete()
