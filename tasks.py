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
from rdflib import Graph, URIRef
from tenacity import retry, wait_exponential, stop_after_attempt
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


async def _seed_wikidata():
    database_url = os.getenv("DATABASE_URL")

    db_connection = await asyncpg.connect(database_url)
    await db_connection.execute("""
        SELECT thing_id FROM things
    """)
    existing_things = set(
        r["thing_id"] for r in await db_connection.fetch("SELECT thing_id FROM things")
    )
    await db_connection.close()

    wikidata: Client = Client()
    image_prop = wikidata.get(EntityId("P18"))

    for line in sys.stdin:
        significance, thing_id = line.split("\t")
        thing_id = thing_id.strip()
        if thing_id in existing_things:
            continue
        entity: Entity = wikidata.get(thing_id, load=True)

        if "en" not in entity.label or "en" not in entity.description:
            continue

        description = entity.description["en"]
        try:
            image: File = entity[image_prop]
        except KeyError:
            continue

        thing = dict(
            thing_id=thing_id,
            label=entity.label["en"],
            description=description,
            significance=int(significance),
            image_url=image.image_url if image else None,
            wikipedia_url=entity.attributes["sitelinks"]["enwiki"]["url"],
        )
        print(json.dumps(thing))


@task
def seed_wikidata(c: Context):
    run(_seed_wikidata())


@retry(wait=wait_exponential(multiplier=2, min=4, max=300), stop=stop_after_attempt(10))
def _get_graph(dbpedia_uri: str) -> Graph:
    graph = Graph()
    graph.parse(dbpedia_uri)
    return graph


@task
def seed_abstract(c: Context):
    for line in sys.stdin:
        entity = json.loads(line)
        wikipedia_url = entity["wikipedia_url"]
        wikipedia_ident = wikipedia_url.split("/")[-1]
        dbpedia_uri = f"http://dbpedia.org/resource/{wikipedia_ident}"

        try:
            graph = _get_graph(dbpedia_uri)
        except Exception as e:
            print(f"Error parsing {dbpedia_uri} -- {e}", file=sys.stderr)
            continue

        for o in graph.objects(
            subject=URIRef(dbpedia_uri),
            predicate=URIRef("http://dbpedia.org/ontology/abstract"),
        ):
            if o.language == "en":
                entity["description"] = o.value
                break

        print(json.dumps(entity))


@task
def seed_llm(c: Context):
    llm: BaseLLM = OllamaLLM(model="gemma3:4b")
    for line in sys.stdin:
        data: Thing = json.loads(line)
        entity: Thing = Thing(**data)
        entity["description"] = markdown.markdown(
            llm.invoke(
                dedent(
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
                )
            ).strip('"')
        )
        print(json.dumps(entity))


async def _seed_db():
    database_url = os.getenv("DATABASE_URL")

    async with asyncpg.create_pool(database_url) as pool:
        for line in sys.stdin:
            thing = Thing(**json.loads(line))

            try:
                async with pool.acquire() as db_connection:
                    await db_connection.execute(
                        """
                        INSERT INTO things (thing_id, label, description, significance, image_url)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT DO NOTHING
                    """,
                        thing["thing_id"],
                        thing["label"],
                        thing["description"],
                        thing["significance"],
                        thing["image_url"],
                    )
            except Exception as e:
                print(f"Error {e} while inserting {thing}", file=sys.stderr)
                continue


@task
def seed_db(c: Context):
    run(_seed_db())
