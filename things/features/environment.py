# -*- coding: utf-8 -*-
import urllib
import urlparse

import httpretty
import mechanize
import os


def before_all(context):

    server_url = context.config.server_url

    def browser_url(url):
        """Create a URL for the virtual WSGI server.

        e.g context.browser_url('/'), context.browser_url(reverse('my_view'))
        """
        return urlparse.urljoin(server_url, url)

    context.url = browser_url

    context.browser = mechanize.Browser()
    context.cookies = mechanize.CookieJar()
    context.browser.set_cookiejar(context.cookies)

    from bs4 import BeautifulSoup
    def soup():
        """Use BeautifulSoup to parse the current response and return the DOM tree.
        """
        r = context.browser.response()
        html = r.read()
        r.seek(0)
        return BeautifulSoup(html)

    context.soup = soup


def after_all(context):
    from django.test import utils
    utils.teardown_test_environment()
    httpretty.disable()
    httpretty.reset()

