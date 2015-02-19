from hamcrest import *
from things.models import Thing, User, Vote
import hyperspace
import requests
import random
import string


@given(u'I am a new visitor')
def new_user(context):
    hyperspace.session.cookies.clear()
    context.user = None
    context.page = hyperspace.jump('http://localhost:5100/things/1')


@given(u'I am not a registered user')
def impl(context):
    User.objects.all().delete()
    new_user(context)


@given(u'I am not logged in')
def impl(context):
    new_user(context)


@given(u'I am a registered user')
def create_user(context):
    hyperspace.session = requests.Session()
    User.objects.all().delete()
    context.user = User.objects.create_user(
        'testuser', 'test@example.com', 'testpassword')
    context.user.save()

    context.page = hyperspace.jump('http://localhost:5100/things/1')
    click_login(context)
    fill_login_form(context)


@then(u'I should be logged in')
def impl(context):
    assert_that(context.page.links['login'], empty())


@when(u'give my username and password')
def fill_login_form(context):
    context.page = context.page.templates['login'][0].build(
        {'login': 'testuser', 'password': 'testpassword'}).submit()


@when(u'click the "Log in" link')
def click_login(context):
    context.page = context.page.links['login'][0].follow()


@when(u'I click the "Register" link')
def click_register(context):
    context.page = context.page.links['register'][0].follow()


@when(u'I give a username and password')
def register(context):
    context.page = context.page.templates['signup'][0].build(
        {'username': 'testuser', 'password1': 'testpassword', 'password2': 'testpassword'}).submit()


@when(u'I try to register with an existing username')
def step_impl(context):
    click_register(context)

    username = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    existing_user = User.objects.create_user(
        username, 'test@example.com', 'testpassword')
    existing_user.save()

    context.page = context.page.templates['signup'][0].build(
        {'username': username, 'password1': 'testpassword', 'password2': 'testpassword'}).submit()


@then(u'I should get an error messaging explaining that username is taken')
def step_impl(context):
    assert_that(context.page.response.content, contains_string('taken'))


@when(u'I register successfully')
def step_impl(context):
    click_register(context)
    register(context)

@then(u'my anonymous votes should be linked to my new account')
def step_impl(context):
    thing = Thing.objects.filter(iri='http://dbpedia.org/resource/Kevin_Bacon')[0]
    thing.set_lang('en')
    user = User.objects.all()[0]
    assert 1 == Vote.objects.filter(
        thing=thing, sentiment=Vote.LIKE, user=user).count()
