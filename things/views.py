from django.http import HttpResponse
from django.shortcuts import render, redirect
from lazysignup.decorators import allow_lazy_user
from things.models import Thing, Vote, User


@allow_lazy_user
def thing_view(request, thing_id):
    thing = Thing.get('dbpedia_' + thing_id)
    return render(request, "thing.html", {'thing': thing, 'user_id': request.user.id})


@allow_lazy_user
def likes(request, thing_id, user_id):
    thing = Thing.get('dbpedia_' + thing_id)
    user = User.objects.get(id=user_id)

    already_voted = not (0 == Vote.objects.filter(
        thing=thing, sentiment='L', user=user).count())

    if already_voted:
        return HttpResponse(status=409)
    else:
        vote = Vote(thing=thing, user=user, sentiment=Vote.LIKE)
        vote.save()

    return redirect(thing)
