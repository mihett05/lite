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

            async def undefined_function(request):
                response = route["handler"](request)
                return {
                    dict: web.Response(text=json.dumps(response), content_type="application/json"),
                    str: web.Response(text=str(response), content_type="text/html")
                }.setdefault(type(response), web.Response(text=str(response), content_type="text/plain"))

            for method in route["methods"]:
                {
                    "get": lambda: self.app.router.add_get(route["path"], undefined_function),
                    "post": lambda: self.app.router.add_post(route["path"], undefined_function),
                    "put": lambda: self.app.router.add_put(route["path"], undefined_function),
                    "delete": lambda: self.app.router.add_delete(route["path"], undefined_function)
                }.setdefault(method.lower(), lambda: self.app.router.add_options(route["path"], undefined_function))()
        web.run_app(self.app)


def send_file(filename):
    with open(filename) as f:
        return f.read()
