import urlparse
import doyoulikeit
from splinter.browser import Browser
from urlparse import urljoin
from splinter.request_handler.status_code import HttpResponseError
import httpretty
import requests
import os


urls = [
    'http://dbpedia.org/resource/Kevin_Bacon',
    'http://dbpedia.org/resource/Roman_Empire',
    'http://dbpedia.org/resource/Cleopatra',
    'http://dbpedia.org/resource/Saturnalia',
    'http://dbpedia.org/resource/Errol_Brown',
]


class Client:
    page = None

    def __init__(self, server_url):
        self.server_url = server_url

    def visit(self, relative_url):
        hyperspace.jump(urljoin(self.server_url, relative_url))


def before_all(context):
    httpretty.enable()
    s = requests.Session()

    for url in urls:
        local_path = os.path.join('things/features/fixtures', url.lstrip('http://'))

        if not os.path.exists(local_path):
            print "Need to acquire fixture for: " + url
            parent = os.path.dirname(local_path)
            if not os.path.exists(parent):
                os.makedirs(parent)

            with open(local_path, 'w') as new_fixture:
                new_fixture.write(s.get(url).content)

        with open(local_path, 'rb') as fixture:
            print "Mocking: " + url
            httpretty.register_uri(httpretty.GET, url, body=fixture.read(), status=200, content_type='text/turtle')

    server_url = context.config.server_url
    context.client = Client(server_url)

def visit_wrapper(context):
    server_url = context.config.server_url
    original_visit = context.browser.visit

    def new_visit(url):
        full_url = urljoin(server_url, url)
        try:
            original_visit(full_url)
        except HttpResponseError, http_error:
            print context.browser.html
            raise http_error

    return new_visit



def after_all(context):
    httpretty.disable()
    httpretty.reset()
