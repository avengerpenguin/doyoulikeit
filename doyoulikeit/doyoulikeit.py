from kule import Kule, jsonify
from bottle import abort, response, route, post, redirect
from SPARQLWrapper import SPARQLWrapper, JSON
import json
from bottle.ext.pystache import view
import mimerender
import pystache
import os
from cork import Cork
from cork.backends import MongoDBBackend
from beaker.middleware import SessionMiddleware


render_html = lambda **args: pystache.render(
    open(os.path.join(os.path.dirname(__file__), 'thing.mustache')).read(),
    dict(args))
render_json = lambda **args: json.dumps(args)

mimerender = mimerender.BottleMimeRender()

session_opts = {
    'session.cookie_expires': True,
    'session.encrypt_key': 'please use a random key and keep it secret!',
    'session.httponly': True,
    'session.timeout': 3600 * 24,  # 1 day
    'session.type': 'cookie',
    'session.validate_key': True,
}


class DoYouLikeIt(Kule):

    def __init__(self, database='doyoulikeit', host='localhost', port=27017,
                 collections=None):
        """
        Overridden from Kule so as to initialise Cork straight after
        MongoDB is set up.
        """
        super(DoYouLikeIt, self).__init__(
            database=database, host=host, port=port, collections=collections)

        self.aaa = Cork(
            backend=MongoDBBackend(
                db_name=database, hostname=host, port=port, initialize=True))

    @mimerender(
        default='html',
        html=render_html,
        json=render_json,
        )
    def get_things_detail(self, pk):
        """
        Fetches a thing from the local store, falling back to
        a remote fetch if that fails. Lastly returns 404 if
        both fail.
        """
        cursor = self.get_collection('things')
        data = cursor.find_one({"thing_id": pk}
            ) or self.fetch_remote(pk) or abort(404)

        del data['_id']
        return data

    def fetch_remote(self, thing_id):
        """
        Gets a thing from DBpedia. Useful for fetching something that
        does't exist in the local store.
        """
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery("""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?title ?description
WHERE {
  <http://dbpedia.org/resource/%(thing_id)s> rdfs:label ?title .
  <http://dbpedia.org/resource/%(thing_id)s> rdfs:comment ?description
  FILTER (lang(?title) = "en")
  FILTER (lang(?description) = "en")
}
""" % {'thing_id': thing_id})

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            new_thing = {
                'thing_id': thing_id,
                'title': result['title']['value'],
                'description': result['description']['value'],
                'popularity': 0.0
                }
            break

        if new_thing:
            collection = self.get_collection('things')
            inserted = collection.insert(new_thing)
            response.status = 201
            new_thing['_id'] = inserted

        return new_thing

    def like_thing(self, thing_id):
        things = self.get_collection('things')
        thing = things.find_one({"thing_id": thing_id}
            ) or self.fetch_remote(pk) or abort(404)

        things.update(
            {"_id": thing['_id']},
            {"$inc": {'likes': 1}}
            )

        redirect('/things/%s' % thing_id, code=302)

    def login():
        """Authenticate users"""
        username = post_get('username')
        password = post_get('password')
        aaa.login(username, password, success_redirect='/',
                  fail_redirect='/login')

    def dispatch_views(self):
        super(DoYouLikeIt, self).dispatch_views()
        self.app.route(
            '/things/:thing_id/like', method='post')(self.like_thing)
        self.app.route('/login', method='post')(self.login)

    def after_request(self):
        """
        Overridden from Kule because that was hard-coding JSON Content-Type
        """
        methods = 'PUT, PATCH, GET, POST, DELETE, OPTIONS'
        headers = 'Origin, Accept, Content-Type'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = methods
        response.headers['Access-Control-Allow-Headers'] = headers

    def get_detail(self, collection, pk):
        """
        Despatches to a method in the form get_XXX_detail because
        simply creating a magic method of that form doesn't seem
        to work with Kule as it currently stands.
        """
        return getattr(self, 'get_%s_detail' % collection)(pk)

    def get_bottle_app(self):
        app = super(DoYouLikeIt, self).get_bottle_app()
        return SessionMiddleware(app, session_opts)

if __name__ == "__main__":
    DoYouLikeIt(database="doyoulikeit").run()
