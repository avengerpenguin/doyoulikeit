from hamcrest import *
from things.models import User


@given(u'I am a new visitor')
def new_user(context):
    context.cookies.clear()


@given(u'I am not a registered user')
def impl(context):
    new_user(context)


@given(u'I am not logged in')
def impl(context):
    new_user(context)


@given(u'I am a registered user')
def impl(context):
    context.cookies.clear()
    User.objects.all().delete()
    context.user = User.objects.create_user(
        'testuser', 'test@example.com', 'testpassword')
    context.user.save()

    br = context.browser
    br.open(context.url('/things/1'))
    click_login(context)
    fill_login_form(context)


@then(u'I should be logged in')
def impl(context):
    assert_that(list(context.browser.links(url_regex='.*/accounts/login.*')), empty())


@when(u'give my username and password')
def fill_login_form(context):
    br = context.browser
    br.select_form(name='login')
    br['username'] = 'testuser'
    br['password'] = 'testpassword'
    br.submit()


@when(u'click the "Log in" link')
def click_login(context):
    br = context.browser
    br.follow_link(text_regex='Log in')


@when(u'I click the "Register" link')
def click_register(context):
    br = context.browser
    br.follow_link(text_regex='Register')


@when(u'I try to register with an existing username')
def impl(context):
    existing = User.objects.all()[0].username
    click_register(context)
    br = context.browser
    br.select_form(name='login')
    br['username'] = existing
    br['password'] = 'somepassword'
    br.submit()

@then(u'I should get an error messaging explaining that username is taken')
def impl(context):
    page = context.browser.response.soup
    assert_that(page.find('p', {'class': 'error'}).text, contains_string('taken'))

@when(u'I register successfully')
def register(context):
    click_register(context)
    br = context.browser
    br.select_form(name='login')
    br['username'] = 'someuser'
    br['password'] = 'somepassword'
    br.submit()

@then(u'my anonymous votes should be linked to my new account')
def impl(context):
    user = User.objects.get(username='someuser')

