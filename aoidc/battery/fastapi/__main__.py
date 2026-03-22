import json
import logging
from contextlib import asynccontextmanager

import structlog
from structlog.stdlib import get_logger

from aoidc.oidc.oidc import OIDCClient
from fastapi import Depends, FastAPI

from . import OpenIdConnectBetter

structlog.stdlib.recreate_defaults()
log = get_logger("fastapi")
logging.getLogger("httpcore").setLevel(logging.ERROR)

raw_provider = json.loads(open("testing.json").read())[-1]
CLIENT_ID = raw_provider["client_id"]
CLIENT_SECRET = raw_provider["client_secret"]
DISCOVERY = raw_provider["url"]


oidc = OpenIdConnectBetter(
    oidc=OIDCClient(
        discovery_endpoint=DISCOVERY,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await oidc.init()
    yield


app = FastAPI(
    debug=True,
    name="Debug APP",
    docs_url="/",
    lifespan=lifespan,
)


@app.get("/get_authed")
async def get_authed(auth=Depends(oidc)) -> str:  # noqa: B008
    log.info("get_authed", auth=auth)
    return "ok"
