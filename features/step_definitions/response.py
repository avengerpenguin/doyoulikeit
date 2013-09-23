from lettuce import *
from nose.tools import assert_equals, assert_less


@step(u'Then the response "([^"]*)" should be "([^"]*)"')
def check_response_key_value(step, key, value):
    assert_equals(value, world.response[key])


@step(u'Then the response "([^"]*)" should be over 50 characters in length')
def check_response_property_is_long(step, key):
    assert_less(50, len(world.response[key]))


@step(u'Then the response "([^"]*)" should be a number')
def check_number_field(step, key):
    assert_equals(float, type(world.response[key]))


@step(u'Then the response should be a list')
def check_response_is_list(step):
    assert_equals(list, type(world.response))


@step(u'Then the response should be status (\d+)')
def then_the_response_should_be_status(step, status):
    assert_equals(int(status), world.raw_response.status_code)


@step(u'And the response should have "([^"]*)" header matching "([^"]*)"')
def check_response_header(step, header, regex_pattern):
    assert header in world.raw_response
    message = '%s does not match %s' % (
        world.raw_response[header], regex_pattern)
    assert re.match(regex_pattern, world.raw_response[header]), message
