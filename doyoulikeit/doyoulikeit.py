from kule import Kule, jsonify
from bottle import abort, response
from SPARQLWrapper import SPARQLWrapper, JSON
import json
from bottle.ext.pystache import view
import mimerender
import pystache
import os


render_html = lambda **args: pystache.render(
    open(os.path.join(os.path.dirname(__file__), 'thing.mustache')).read(),
    dict(args))
render_json = lambda **args: json.dumps(args)

mimerender = mimerender.BottleMimeRender()


class DoYouLikeIt(Kule):
    def get_detail(self, collection, pk):
        """
        Despatches to a method in the form get_XXX_detail because
        simply creating a magic method of that form doesn't seem
        to work with Kule as it currently stands.
        """
        return getattr(self, 'get_%s_detail' % collection)(pk)

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
SELECT ?label
WHERE {
  <http://dbpedia.org/resource/%s> rdfs:label ?label
  FILTER (lang(?label) = "en")
}
""" % thing_id)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results["results"]["bindings"]:
            new_thing = {
                'thing_id': thing_id,
                'title': result['label']['value']
                }
            break

        if new_thing:
            collection = self.get_collection('things')
            inserted = collection.insert(new_thing)
            response.status = 201
            new_thing['_id'] = inserted

        return new_thing

    def after_request(self):
        """
        Overridden from Kule because that was hard-coding JSON Content-Type
        """
        methods = 'PUT, PATCH, GET, POST, DELETE, OPTIONS'
        headers = 'Origin, Accept, Content-Type'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = methods
        response.headers['Access-Control-Allow-Headers'] = headers

if __name__ == "__main__":
    DoYouLikeIt(database="doyoulikeit").run()
