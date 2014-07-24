import urlparse
import doyoulikeit
from splinter.browser import Browser
from urlparse import urljoin


def visit_wrapper(context):
    server_url = context.config.server_url
    original_visit = context.browser.visit

    def new_visit(url):
        full_url = urljoin(server_url, url)
        original_visit(full_url)

    return new_visit


def before_all(context):
    context.browser = Browser(driver_name='phantomjs')

    context.browser.visit = visit_wrapper(context)


def after_all(context):
    context.browser.quit()
    context.browser = None
