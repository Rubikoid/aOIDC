import asyncio
import json
import logging
import secrets

import h11
import structlog
from httpx import URL
from structlog.stdlib import get_logger

from .oidc.oidc import OIDCClient

structlog.stdlib.recreate_defaults()
log = get_logger("test")
logging.getLogger("httpcore").setLevel(logging.ERROR)

raw_provider = json.loads(open("testing.json").read())[-1]
CLIENT_ID = raw_provider["client_id"]
CLIENT_SECRET = raw_provider["client_secret"]
DISCOVERY = raw_provider["url"]


async def run_handler(*, port: int) -> tuple[int, asyncio.Future[str], asyncio.Task]:  # noqa: C901, PLR0915
    MAX_RECV = 2**16
    TIMEOUT = 10

    future: asyncio.Future[str] = asyncio.Future()

    async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        remote_addr = writer.get_extra_info("peername")
        remote_ip, remote_port, *_ = remote_addr

        _log = log.bind(remote_ip=remote_ip, remote_port=remote_port)

        conn = h11.Connection(h11.SERVER)
        events = []

        async with asyncio.timeout(TIMEOUT):
            conn.receive_data(await reader.read(MAX_RECV))
            while True:
                try:
                    event = conn.next_event()
                    if event is h11.NEED_DATA:
                        conn.receive_data(await reader.read(MAX_RECV))
                        continue

                    events.append(event)

                    # An EndOfMessage event signifies the end of the request
                    if isinstance(event, h11.EndOfMessage):
                        break

                except h11.ProtocolError:
                    _log.exception()
                    break

        request_event = next((e for e in events if isinstance(e, h11.Request)), None)

        if request_event:
            _log.info("Got request!", method=request_event.method, target=request_event.target)
            target = request_event.target.decode("utf-8")
            future.set_result(target)
        else:
            future.set_exception(Exception)

        body = b"""ok <script type="text/javascript">setTimeout(function(){window.close();},1000);</script>"""
        es = [
            h11.Response(
                status_code=200,
                headers=[
                    ("Content-Type", "text/html; charset=utf-8"),
                    ("Content-Length", str(len(body))),
                    ("Server", "test"),
                ],
            ),
            h11.Data(data=body),
            h11.EndOfMessage(),
        ]

        for e in es:
            serialized = conn.send(e)

            if not serialized:
                break

            writer.write(serialized)

        await writer.drain()
        writer.close()
        await writer.wait_closed()  # Ensure the writer is closed

    server = await asyncio.start_server(
        handle_client,
        "0.0.0.0",
        port,
    )

    for socket in server.sockets:
        _v = socket.getsockname()
        host, port, *_ = _v
        break

    log.info("Starting handler", port=port)

    async def srv_task():
        async with server:
            await server.serve_forever()

    srv = asyncio.create_task(srv_task())

    async def watcher_task():
        await future
        srv.cancel()

    watcher = asyncio.create_task(watcher_task())

    return port, future, watcher  # pyright: ignore[reportPossiblyUnboundVariable]


async def main():
    # for CLIENT_ID, CLIENT_SECRET, DISCOVERY in public_tests:
    client = OIDCClient(discovery_endpoint=DISCOVERY, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    await client.init()

    port, future, w = await run_handler(port=9999)

    redirect_uri = f"http://127.0.0.1:{port}"
    state = secrets.token_urlsafe(nbytes=16)

    auth_link = await client.authorization_code_flow_start(redirect_uri=redirect_uri, state=state)
    log.warning("Starting auth code flow with", link=auth_link)

    # subprocess.run(
    #     [
    #         "/mnt/c/Program Files/Vivaldi/Application/vivaldi.exe",
    #         str(auth_link),
    #     ],
    # )
    # input("..?")

    # link = input("Enter link: ")
    link = await future
    parsed_link = URL(link)

    token = await client.authorization_code_flow_continue(
        code=parsed_link.params["code"],
        state=parsed_link.params["state"],
        redirect_uri=redirect_uri,
    )

    id_token = await client.authorization_code_flow_finalize(token)
    log.info("ID token", id_token=id_token)

    userinfo = await client.userinfo(token.access_token)
    log.info("userinfo", userinfo=userinfo)


if __name__ == "__main__":
    asyncio.run(main())
