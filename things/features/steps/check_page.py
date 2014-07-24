from behave import *

@then(u'the page should have the title "{title}"')
def impl(context, title):
    page_h1 = context.browser.find_by_tag('h1').first
    assert title == page_h1.text, "Page should contain h1 '%s', has '%s'" % (title, page_h1.text)
