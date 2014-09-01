from behave import *
from things.models import Thing, User, Vote


@then(u'the site should register my like for "{title}"')
def impl(context, title):
    thing = Thing.get('dbpedia_' + title.replace(' ', '_'))
    assert 1 == Vote.objects.filter(thing=thing, sentiment='L', user=context.user).count


@then(u'there should be no "Yes" button')
def impl(context):
    assert len(context.browser.find_by_value('Yes')) == 0


@when(u'I click the "Yes" button')
def impl(context):
    context.browser.find_by_value('Yes')[0].click()


@given(u'I have previously liked "{title}"')
def impl(context, title):

    thing = Thing.get('dbpedia_' + title.replace(' ', '_'))

    if 0 == Vote.objects.filter(thing=thing, sentiment='L', user=context.user).count:
        vote = Vote()
        vote.thing = Thing.get('dbpedia_' + title.replace(' ', '_'))
        vote.user = context.user
        vote.save()

    assert 1 == Vote.objects.filter(thing__rdfs_label=title, sentiment='L', user__id=context.user.id).count
