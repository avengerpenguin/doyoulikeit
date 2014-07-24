from django.http import HttpResponse
from django.shortcuts import render
from things.models import Thing

# Create your views here.

def thing(request, thing_id):
    thing = Thing.get(thing_id)
    return HttpResponse('<h1>{title}</h1>'.format(title=thing.title))
