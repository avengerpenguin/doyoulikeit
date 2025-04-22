import json
import os
import random
from textwrap import dedent

import markdown
from langchain_core.language_models import BaseLLM
from langchain_ollama import OllamaLLM
from quart import Quart, g, render_template, redirect, make_response, request, Response
from quart_db import QuartDB
from rdflib import Graph, URIRef, Literal
from typing_extensions import TypedDict
from werkzeug.exceptions import NotFound
from wikidata.client import Client
from wikidata.commonsmedia import File
from wikidata.entity import Entity, EntityId
from jinja2_fragments.quart import render_block


app: Quart = Quart(__name__, template_folder="templates")
db: QuartDB = QuartDB(app, url=os.getenv("DATABASE_URL", "sqlite:memory:"))
wikidata: Client = Client()
image_prop = wikidata.get(EntityId('P18'))



# with open("films.json") as f:
#     data = json.load(f)
#     ALL_THE_THINGS = set(
#         row["item"].split("/")[-1]
#         for row in data
#     )

ALL_THE_THINGS = set()

# with open("things.json") as f:
#     data = json.load(f)
#     for result in data["results"]["bindings"]:
#         ALL_THE_THINGS.add(result["other"]["value"].split("/")[-1])


with open("filtered.tsv") as f:
    for line in f:
        _, thing_id = line.split("\t")
        ALL_THE_THINGS.add(thing_id.strip())


@app.route('/')
async def index():
    new_thing = await random_thing()
    return redirect(f"/{new_thing}")


async def random_thing():
    results = await g.connection.fetch_all("SELECT thing_id FROM votes WHERE user_id = '1'")
    seen_things = set(row["thing_id"] for row in results)
    new_thing = random.choice(list(ALL_THE_THINGS - seen_things))
    return new_thing


class Thing(TypedDict):
    thing_id: str
    label: str
    description: str
    image_url: str | None


async def get_thing(thing_id: EntityId) -> Thing | None:
    result = await g.connection.fetch_one("""
    SELECT thing_id, label, description, image_url FROM things WHERE thing_id = :thing_id
    """, {"thing_id": thing_id}
    )
    if result:
        return Thing(**result)


@app.get('/<string:thing_id>')
async def thing_view(thing_id: EntityId):
    thing = await get_thing(thing_id)

    if thing is None:
        return Response(status=404)

    if request.headers.get("HX-Request"):
        return await render_block("thing.html", "content", thing=thing)

    return await render_template("thing.html", thing=thing)


@app.post('/<string:thing_id>/like')
async def vote_like(thing_id: EntityId):
    await g.connection.execute(
        """
        INSERT INTO votes
        (user_id, thing_id, liked)
        VALUES
        (1, :thing_id, true)
        ON CONFLICT (user_id, thing_id) DO UPDATE SET liked = true
        """,
        {"thing_id": thing_id},
    )

    new_thing = await random_thing()

    if request.headers.get("HX-Request"):
        response = await make_response()
        response.headers["HX-Location"] = json.dumps({"path": f"/{new_thing}", "target": "main"})
        return response

    return redirect(f"/{new_thing}")


@app.post('/<string:thing_id>/skip')
async def vote_skip(thing_id: EntityId):
    await g.connection.execute(
        """
        INSERT INTO votes
        (user_id, thing_id, liked)
        VALUES
        (1, :thing_id, false)
        ON CONFLICT (user_id, thing_id) DO UPDATE SET liked = false
        """,
        {"thing_id": thing_id},
    )

    new_thing = await random_thing()

    if request.headers.get("HX-Request"):
        response = await make_response()
        response.headers["HX-Location"] = json.dumps({"path": f"/{new_thing}", "target": "main"})
        return response

    return redirect(f"/{new_thing}")
