from lettuce import *
import json


@step(u'When I GET "([^"]*)"')
def when_i_get_group1(step, path):
    world.response = world.app.get(
        path, headers={'Accept': 'application/json'}).json
