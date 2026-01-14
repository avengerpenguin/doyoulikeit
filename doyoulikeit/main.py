import json
import os
from urllib.parse import urlencode, quote_plus
import pydash

from jinja2_fragments.quart import render_block
from quart import (
    Quart,
    g,
    render_template,
    redirect,
    make_response,
    request,
    Response,
    url_for,
    session,
)
from quart_authlib import OAuth
from quart_db import QuartDB
from typing_extensions import TypedDict
from wikidata.client import Client
from wikidata.entity import EntityId
import sentry_sdk
from sentry_sdk.integrations.quart import QuartIntegration


app: Quart = Quart(__name__, template_folder="templates")
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
db: QuartDB = QuartDB(app, url=os.getenv("DATABASE_URL", "sqlite:memory:"))
wikidata: Client = Client()
image_prop = wikidata.get(EntityId("P18"))

print(os.getenv("SENTRY_DSN"))
sentry_sdk.init(
    integrations=[QuartIntegration()],
)

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

@app.before_request
async def redirect_www():
    host = request.host
    if host and host.startswith("www."):
        new_host = host[4:]
        url = f"{request.scheme}://{new_host}{request.full_path}"
        return redirect(url, code=301)
    return None


@app.route("/login")
async def login():
    redirect_uri = url_for("callback", _external=True)
    return oauth.auth0.authorize_redirect(redirect_uri)


@app.route("/callback", methods=["GET", "POST"])
async def callback():
    token = await oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + os.getenv("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": os.getenv("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/")
async def home():
    user_id = pydash.get(session, "user.userinfo.sub")
    new_thing = await random_thing(user_id)
    return redirect(f"/{new_thing}")


class Thing(TypedDict):
    thing_id: str
    label: str
    description: str
    significance: int
    image_url: str | None


async def random_thing(user_id: str | None) -> str | None:
    if user_id:
        result = await g.connection.fetch_one(
            """
        SELECT t.thing_id
        FROM things t
        LEFT JOIN votes v
        ON t.thing_id = v.thing_id AND v.user_id = :user_id
        WHERE v.thing_id IS NULL
        ORDER BY RANDOM() * LOG(t.significance + 1) DESC
        LIMIT 1;
        """,
            {"user_id": user_id},
        )
    else:
        result = await g.connection.fetch_one("""
        SELECT t.thing_id
        FROM things t
        ORDER BY RANDOM() * LOG(t.significance + 1)
 DESC
        LIMIT 1;
        """)
    if result:
        return result["thing_id"]
    return None


async def get_thing(thing_id: EntityId) -> Thing | None:
    result: Thing = await g.connection.fetch_one(
        """
    SELECT thing_id, label, description, image_url FROM things WHERE thing_id = :thing_id
    """,
        {"thing_id": thing_id},
    )
    if result:
        return Thing(**result)
    return None


@app.get("/<string:thing_id>")
async def thing_view(thing_id: EntityId):
    thing = await get_thing(thing_id)

    if thing is None:
        return Response(status=404)

    if request.headers.get("HX-Request"):
        return await render_block("thing.html", "content", thing=thing)

    return await render_template("thing.html", thing=thing, session=session.get("user"))


@app.post("/<string:thing_id>/like")
async def vote_like(thing_id: EntityId):
    user_id = pydash.get(session, "user.userinfo.sub")
    if not user_id:
        return redirect(f"/{thing_id}")

    await g.connection.execute(
        """
        INSERT INTO votes
        (user_id, thing_id, liked)
        VALUES
        (:user_id, :thing_id, true)
        ON CONFLICT (user_id, thing_id) DO UPDATE SET liked = true
        """,
        {"thing_id": thing_id, "user_id": user_id},
    )

    new_thing = await random_thing(user_id)

    if request.headers.get("HX-Request"):
        response = await make_response()
        response.headers["HX-Location"] = json.dumps(
            {"path": f"/{new_thing}", "target": "main"}
        )
        return response

    return redirect(f"/{new_thing}")


@app.post("/<string:thing_id>/skip")
async def vote_skip(thing_id: EntityId):
    user_id = pydash.get(session, "user.userinfo.sub")
    if not user_id:
        return redirect(f"/{thing_id}")

    await g.connection.execute(
        """
        INSERT INTO votes
        (user_id, thing_id, liked)
        VALUES
        (:user_id, :thing_id, false)
        ON CONFLICT (user_id, thing_id) DO UPDATE SET liked = false
        """,
        {"thing_id": thing_id, "user_id": user_id},
    )

    new_thing = await random_thing(user_id)

    if request.headers.get("HX-Request"):
        response = await make_response()
        response.headers["HX-Location"] = json.dumps(
            {"path": f"/{new_thing}", "target": "main"}
        )
        return response

    return redirect(f"/{new_thing}")
