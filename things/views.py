from django.http import HttpResponse
from django.shortcuts import render
from things.models import Thing


def thing_view(request, thing_id):
    thing = Thing.get('dbpedia_' + thing_id)
    return render(request, "thing.html", {'thing': thing})
