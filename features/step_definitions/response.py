from lettuce import *
from nose.tools import assert_equals, assert_less


@step(u'Then the response "([^"]*)" should be "([^"]*)"')
def check_response_key_value(step, key, value):
    assert_equals(value, world.response[key])
