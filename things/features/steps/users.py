from behave import *
from django.contrib.auth.models import AnonymousUser
from things.models import User

@given(u'I am a new visitor')
def impl(context):
    context.browser.cookies.delete()
    context.user = AnonymousUser()


@given(u'I am a registered user')
def impl(context):
    context.user = User()
    context.user.save()
