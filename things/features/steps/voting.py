from behave import *

@then(u'the site should register my like for "Saturnalia"')
def impl(context):
    assert False


@then(u'there should be no "Yes" button')
def impl(context):
    assert len(context.browser.find_by_value('Yes')) == 0
