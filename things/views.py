from django.http import HttpResponse
from django.shortcuts import render, redirect
from things.models import Thing, Vote, User
from allauth.account.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def reparent_after_login(sender, **kwargs):
    request = kwargs['request']
    user = kwargs['user']
    Vote.reparent_all_my_session_objects(request.session, user)


def thing_view(request, thing_id):

    thing = Thing.objects.get(id=int(thing_id))
    thing.set_lang('en')

    if request.user.is_anonymous():
        already_voted = (Vote.get_stashed_in_session(request.session).filter(thing=thing).count() > 0)
        user_id = 0
    else:
        already_voted = not (0 == Vote.objects.filter(
            thing=thing, sentiment=Vote.LIKE, user__id=request.user.id).count())
        user_id = request.user.id


    return render(request, "thing.html", {
        'thing': thing,
        'user_id': user_id,
        'already_voted': already_voted
    })


def bounce(request):
    iri = request.GET['iri']

    if not iri:
        return HttpResponse(status=404)

    thing = Thing.get_or_create(iri)

    if len(thing._graph) == 0:
        thing.delete()
        return HttpResponse(status=404)

    return redirect(thing)


def thing_redirect(_request, thing_id):
    iri = u'http://dbpedia.org/resource/{}'.format(thing_id)
    thing = Thing.get_or_create(iri)

    if len(thing._graph) == 0:
        thing.delete()
        return HttpResponse(status=404)
    return redirect(thing)


def likes(request, thing_id, user_id):
    thing = Thing.objects.get(id=int(thing_id))

    if int(user_id) > 0:
        user = User.objects.get(id=user_id)

        if request.user != user:
            return HttpResponse(status=403)

        already_voted = not (0 == Vote.objects.filter(
            thing=thing, user=user).count())

        if already_voted:
            return HttpResponse(status=409)
        else:
            vote = Vote(thing=thing, user=user, sentiment=Vote.LIKE)
            vote.save()

    else:
        already_voted = Vote.get_stashed_in_session(request.session).filter(thing=thing).count() > 0
        if already_voted:
            return HttpResponse(status=409)
        else:
            vote = Vote(thing=thing, sentiment=Vote.LIKE)
            vote.save()
            vote.stash_in_session(request.session)

    return redirect(thing)
