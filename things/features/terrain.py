from lettuce import *
from webtest import TestApp
from doyoulikeit import DoYouLikeIt
import bottle
import pymongo


@before.all
def create_app():
    global DEBUG
    bottle.debug()
    dyli = DoYouLikeIt(database='doyoulikeit_test')
    world.app = TestApp(dyli.get_bottle_app())


@before.all
def clear_mongo():
    connection = pymongo.Connection()
    db = connection['doyoulikeit_test']
    db.things.remove()
