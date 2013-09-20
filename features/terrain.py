from lettuce import *
from webtest import TestApp
from doyoulikeit import DoYouLikeIt
import bottle


@before.all
def create_app():
    global DEBUG
    bottle.debug()
    dyli = DoYouLikeIt(database='doyoulikeit_test')
    world.app = TestApp(dyli.get_bottle_app())
