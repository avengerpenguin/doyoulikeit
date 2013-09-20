from kule import Kule, jsonify
from bottle import abort, response
from SPARQLWrapper import SPARQLWrapper, JSON
import json


class DoYouLikeIt(Kule):
    def get_detail(self, collection, pk):
        return getattr(self, 'get_%s_detail' % collection)(pk)

    def get_things_detail(self, pk):
        cursor = self.get_collection('things')
        data = cursor.find_one({"thing_id": pk}
            ) or self.fetch_remote(pk) or abort(404)

        del data['_id']
        return jsonify(data)

    def fetch_remote(self, thing_id):
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


if __name__ == "__main__":
    DoYouLikeIt(database="doyoulikeit").run()
