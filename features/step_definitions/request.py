from lettuce import *
import json


@step(u'When I GET "([^"]*)"')
def when_i_get_group1(step, path):
    world.response = world.app.get(
        path, headers={'Accept': 'application/json'}).json


@step(u'When I POST to "([^"]*)"')
def when_i_post_to_group1(step, path):
    world.raw_response = world.app.post(
        str(path), headers={'Accept': 'application/json'})
    world.response = world.raw_response.json


@step(u'Given I am a new visitor')
def given_i_am_a_new_visitor(step):
    world.app.reset()
