import asyncio

import requests
import uvloop
from aiohttp import web

import aiomonitor


async def simple(request):
    loop = request.app.loop
    await asyncio.sleep(10, loop=loop)
    return web.Response(text="Simple answer")


async def hello(request):
    resp = web.StreamResponse()
    name = request.match_info.get("name", "Anonymous")
    answer = ("Hello, " + name).encode("utf8")
    resp.content_length = len(answer)
    resp.content_type = "text/plain"
    await resp.prepare(request)
    await asyncio.sleep(10, loop=loop)
    await resp.write(answer)
    await resp.write_eof()
    return resp


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_get("/simple", simple)
    app.router.add_get("/hello/{name}", hello)
    app.router.add_get("/hello", hello)
    return app


host, port = "localhost", 8090
loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)
app = loop.run_until_complete(init(loop))


class WebMonitor(aiomonitor.Monitor):
    def do_hello(self, sin, sout, name=None):
        """Using the /hello GET interface

        There is one optional argument, "name".  This name argument must be
        provided with proper URL excape codes, like %20 for spaces.
        """
        name = "" if name is None else "/" + name
        r = requests.get("http://localhost:8090/hello" + name)
        sout.write(r.text + "\n")


with aiomonitor.start_monitor(loop, monitor=WebMonitor, locals=locals()):
    web.run_app(app, port=port, host=host)
