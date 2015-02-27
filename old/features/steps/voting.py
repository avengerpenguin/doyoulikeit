from behave import *
from hamcrest import *
from things.models import Thing, User, Vote
import hyperspace


@then(u'the site should register my like for "{title}"')
def impl(context, title):
    thing = Thing.objects.filter(iri='http://dbpedia.org/resource/' + title.replace(' ', '_'))[0]
    thing.set_lang('en')
    if context.user:
        assert 1 == Vote.objects.filter(
            thing=thing, sentiment=Vote.LIKE, user=context.user).count()
    else:
        assert 1 == Vote.objects.filter(
            thing=thing, sentiment=Vote.LIKE).count()


@then(u'there should be no "Yes" button')
def impl(context):
    assert_that(list(context.page.templates), empty())


@when(u'I click the "Yes" button')
def click_yes(context):
    context.page = context.page.templates['like'][0].submit()


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


@given(u'I have been voting on some things anonymously')
def impl(context):
    Vote.objects.all().delete()
    hyperspace.session.cookies.clear()
    context.user = None
    context.page = hyperspace.jump('http://localhost:5100/things/1')
    click_yes(context)
