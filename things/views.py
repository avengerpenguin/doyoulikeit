from django.http import HttpResponse
from django.shortcuts import render, redirect
from things.models import Thing, Vote, User


def thing_view(request, thing_id):
    thing = Thing.get('dbpedia_' + thing_id)
    return render(request, "thing.html", {'thing': thing, 'user_id': request.user.id or request.session.session_key})


def likes(request, thing_id, user_id):
    thing = Thing.get('dbpedia_' + thing_id)
    user = User.objects.get(username=user_id)

    already_voted = bool(
        Vote.objects.filter(thing=thing, sentiment='L', user=user).count)

    if already_voted:
        return HttpResponse(status=409)
    else:
        vote = Vote()
        vote.thing = Thing.get('dbpedia_' + thing_id)
        vote.user = user
        print vote
        vote.save()

    return redirect(thing)
