from lettuce import *
from nose.tools import assert_equals, assert_less


@step(u'Then the response "([^"]*)" should be "([^"]*)"')
def check_response_key_value(step, key, value):
    assert_equals(value, world.response[key])


@step(u'Then the response "([^"]*)" should be over 50 characters in length')
def check_response_property_is_long(step, key):
    assert_less(50, len(world.response[key]))
