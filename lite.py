from aiohttp import web
import json


class Lite:
    def __init__(self, routes):
        self.routes = routes
        self.app = web.Application()
        for route in routes:
            if "methods" not in route:
                route["methods"] = ["get"]
            route["methods"] = frozenset(route["methods"])

            async def function_wrapper(request):
                req = {
                    "original": request,
                    "params": dict(request.match_info).values(),
                    "query": dict(request.rel_url.query),
                    "method": request.method,
                    "url": request.url,
                    "headers": dict(request.headers),
                    "cookies": dict(request.cookies),
                }
                
                response = route["handler"](req, *req["params"])
                return {
                    dict: web.Response(text=json.dumps(response), content_type="application/json"),
                    str: web.Response(text=str(response), content_type="text/html")
                }.setdefault(type(response), web.Response(text=str(response), content_type="text/plain"))

            for method in route["methods"]:
                {
                    "get": lambda: self.app.router.add_get(route["path"], function_wrapper),
                    "post": lambda: self.app.router.add_post(route["path"], function_wrapper),
                    "put": lambda: self.app.router.add_put(route["path"], function_wrapper),
                    "delete": lambda: self.app.router.add_delete(route["path"], function_wrapper)
                }.setdefault(method.lower(), lambda: self.app.router.add_options(route["path"], function_wrapper))()
        web.run_app(self.app)


def send_file(filename):
    with open(filename) as f:
        return f.read()
