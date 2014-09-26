from django.http import HttpResponse
from django.shortcuts import render, redirect
from lazysignup.decorators import allow_lazy_user
from things.models import Thing, Vote, User


@allow_lazy_user
def thing_view(request, thing_id):

    thing = Thing.get('http://dbpedia.org/resource/' + thing_id)

    already_voted = not (0 == Vote.objects.filter(
        thing=thing, sentiment=Vote.LIKE, user=request.user).count())

    return render(request, "thing.html", {
        'thing': thing,
        'user': request.user,
        'already_voted': already_voted
    })


@allow_lazy_user
def likes(request, thing_id, user_id):
    thing = Thing.get('http://dbpedia.org/resource/' + thing_id)
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

    return redirect(thing)
