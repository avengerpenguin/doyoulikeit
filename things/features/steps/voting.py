from behave import *
from hamcrest import *
from things.models import Thing, User, Vote


@then(u'the site should register my like for "{title}"')
def impl(context, title):
    thing = Thing.objects.filter(iri='http://dbpedia.org/resource/' + title.replace(' ', '_'))[0]
    assert 1 == Vote.objects.filter(
        thing=thing, sentiment=Vote.LIKE).count()


@then(u'there should be no "Yes" button')
def impl(context):
    assert_that(list(context.browser.forms()), empty())


@when(u'I click the "Yes" button')
def impl(context):
    thing_url = context.browser.geturl()
    context.browser.select_form(name='like')
    context.browser.submit()
    assert context.browser.geturl() == thing_url


@given(u'I have previously liked "{title}"')
def impl(context, title):

    iri = 'http://dbpedia.org/resource/' + title.replace(' ', '_')
    try:
        thing = Thing.objects.get(iri=iri)
    except Thing.DoesNotExist, e:
        thing = Thing(iri=iri)
        thing.save()

    if 0 == Vote.objects.filter(thing=thing, sentiment=Vote.LIKE, user=context.user).count():
        vote = Vote(thing=thing, user=context.user, sentiment=Vote.LIKE)
        vote.save()

    assert 1 == Vote.objects.filter(
        thing=thing, sentiment=Vote.LIKE, user=context.user).count()
