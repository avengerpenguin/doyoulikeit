import sys
from pathlib import Path

from invoke import task, Context
from testcontainers.compose import DockerCompose


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
