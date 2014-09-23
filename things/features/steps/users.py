from behave import *
from hamcrest import *
from django.contrib.auth.models import AnonymousUser
from things.models import User
from django.contrib.auth import login


@given(u'I am a new visitor')
def impl(context):
    context.browser.cookies.delete()


@given(u'I am not logged in')
def impl(context):
    context.browser.cookies.delete()


@given(u'I am a registered user')
def impl(context):
    context.browser.cookies.delete()
    User.objects.all().delete()
    context.user = User.objects.create_user(
        'testuser', 'test@example.com', 'testpassword')
    context.user.save()
    context.browser.visit('/accounts/login')
    context.browser.fill('username', 'testuser')
    context.browser.fill('password', 'testpassword')
    context.browser.find_by_value('Log in')[0].click()


@then(u'I should be logged in')
def impl(context):
    assert_that(context.browder.find_by_value('Log in'), has_length(0))


@when(u'give my username and password')
def impl(context):
    context.browser.fill('username', 'testuser')
    context.browser.fill('password', 'testpassword')
    context.browser.find_by_value('Log in')[0].click()


@when(u'click the "Log in" link')
def impl(context):
    context.browser.find_by_value('Log in')[0].click()

