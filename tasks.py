import json
import os
import sys
from asyncio import run
from pathlib import Path
from textwrap import dedent

import asyncpg
import markdown
from invoke import task, Context
from langchain_core.language_models import BaseLLM
from langchain_ollama import OllamaLLM
from rdflib import Graph, URIRef, Literal
from testcontainers.compose import DockerCompose
from wikidata.client import Client
from wikidata.commonsmedia import File
from wikidata.entity import Entity, EntityId

from doyoulikeit.main import Thing


@task
def dev(c: Context):
    with DockerCompose(
        context=Path(__file__).parent,
        compose_file_name=[
            str(Path(__file__).parent / "docker-compose.yml"),
        ],
        wait=False,
    ) as compose:
        stdout, stderr = compose.get_logs("atlas")
        print(stdout)
        print(stderr, file=sys.stderr)

        db_port = compose.get_container("db").get_publisher(5432).PublishedPort
        db_uri = f"postgres://postgres:1234@localhost:{db_port}/doyoulikeit"
        c.run(
            "quart run --reload --port 8080",
            env={
                "QUART_APP": "doyoulikeit:app",
                "QUART_DEBUG": "true",
                "DATABASE_URL": db_uri,
            },
        )


@task
def create_migrations(c: Context):
    c.run("""
        atlas migrate diff create_users \
          --dir "file://migrations" \
          --to "file://db/schema.sql" \
          --dev-url "docker://postgres/17/dev?search_path=public"
    """)


@task
def build(c: Context):
    c.run("docker build -t doyoulikeit .")

@task
def infra(c: Context):
    c.run("tofu -chdir=infra init")
    c.run("tofu -chdir=infra plan")


@task
def seed_wikidata(c: Context):
    wikidata: Client = Client()
    image_prop = wikidata.get(EntityId('P18'))

    for line in sys.stdin:
        significance, thing_id = line.split("\t")
        entity: Entity = wikidata.get(thing_id, load=True)

        try:
            description = entity.description["en"]
        except KeyError:
            continue
        try:
            image: File = entity[image_prop]
        except KeyError:
            image = None

        thing = dict(
            thing_id=thing_id,
            label=entity.label["en"],
            description=description,
            image_url=image.image_url if image else None,
            wikipedia_url = entity.attributes["sitelinks"]["enwiki"]["url"],
        )
        print(json.dumps(thing))


@task
def seed_abstract(c: Context):
    for line in sys.stdin:
        entity = json.loads(line)
        wikipedia_url = entity["wikipedia_url"]
        wikipedia_ident = wikipedia_url.split("/")[-1]
        dbpedia_uri = f"http://dbpedia.org/resource/{wikipedia_ident}"

        graph = Graph()
        try:
            graph.parse(dbpedia_uri)
        except Exception:
            print(f"Error parsing {dbpedia_uri}", file=sys.stderr)
            raise

        for o in graph.objects(subject=URIRef(dbpedia_uri), predicate=URIRef("http://dbpedia.org/ontology/abstract")):
            o: Literal
            if o.language == "en":
                entity["description"] = o.value
                break


@task
def seed_llm(c: Context):
    for line in sys.stdin:
        entity = Thing(**json.loads(line))
        llm: BaseLLM = OllamaLLM(model="gemma3:4b")
        entity["description"] = markdown.markdown(llm.invoke(dedent(
            f"""\
            You are an editor and copywriter for a website and app that presents users with random things and asks
            them to mark which things they like. It's a random, quirky website for seeing what are the most liked
            things in the world in completely separate categories.
    
            I am going to give you an encyclopaedia-style abstract for {entity["label"]} and I want you to rewrite
            this abstract into a style that retains the informative nature in case someone hasn't heard of
            the thing, but has a tone that is trying to hype up the thing to encourage the user to like it.
    
            Please respond with just the copy to put on the page with nothing additional.
    
            Abstract: {entity["description"]}
            """
        )).strip("\""))
        print(json.dumps(entity))


async def _seed_db():
    database_url = os.getenv("DATABASE_URL")

    db_connection = await asyncpg.connect(database_url)
    for line in sys.stdin:
        thing = Thing(**json.loads(line))

        await db_connection.execute("""
            INSERT INTO things (thing_id, label, description, significance, image_url)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT DO NOTHING
        """, thing["thing_id"], thing["label"], thing["description"], int(significance), thing["image_url"])


    await db_connection.close()


@task
def seed_db(c: Context):
    run(_seed_db())
