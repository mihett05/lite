from aiohttp import web
import json
import re


class Lite:
    def __init__(self, routes):
        self.routes = routes
        self.app = web.Application(middlewares=[self.route_handler])
        self.error_handlers = []

        for route in routes:
            if "methods" not in route:
                route["methods"] = ["get"]
            route["methods"] = frozenset(route["methods"])
            route["path"] = "" if route["path"] == "*" else route["path"]
            route["handler"] = self.wrapper(route["handler"])
            if not route["path"][0] == "/" and not route["path"] == "":
                if re.fullmatch(r"\d+", route["path"]) is not None:
                    self.error_handlers.append({
                        "status": route["path"], "methods": route["methods"], "handler": route["handler"]
                    })
                    self.routes.remove(route)

            route["params"] = dict(map(lambda x: (x.split(":")[1],
                                                  self.get_number_of_section(route["path"], "{"+x+"}")),
                                       re.findall(r"{([\s\S]+?)}", route["path"])))
            route["path"] = re.sub(r"{int:([\S]+?)}", r"(\\d+?)", route["path"])
            route["path"] = re.sub(r"{str:([\S]+?)}", r"(.+?)", route["path"])

    @staticmethod
    def get_number_of_section(path, string):
        sections = path.split("/")
        for i in range(len(sections)):
            if sections[i] == string:
                return i

    async def raise_error(self, request, status, exception, for_return=None):
        handlers = list(filter(lambda x: x["status"] == status, self.error_handlers))
        if len(handlers) > 1:
            raise web.HTTPMultipleChoices(request.rel_url)
        elif len(handlers) == 1:
            return await handlers[0]["handler"](request, for_return)
        elif len(handlers) == 0:
            raise exception

    @staticmethod
    def wrapper(func):
        async def function_wrapper(request, params=None):
            req = {
                "original": request,
                "params": params if params is not None else {},
                "query": dict(request.rel_url.query),
                "method": request.method,
                "url": request.url,
                "headers": dict(request.headers),
                "cookies": dict(request.cookies),
            }

            response = func(req, **req["params"])
            return {
                dict: web.Response(text=json.dumps(response), content_type="application/json"),
                list: web.Response(text=json.dumps(response), content_type="application/json"),
                tuple: web.Response(text=json.dumps(response), content_type="application/json"),
                set: web.Response(text=json.dumps(response), content_type="application/json"),
                frozenset: web.Response(text=json.dumps(response), content_type="application/json"),
                str: web.Response(text=str(response), content_type="text/html")
            }.setdefault(type(response), web.Response(text=str(response), content_type="text/plain"))
        return function_wrapper

    @web.middleware
    async def route_handler(self, request, handler=None):
        found_routes = list(filter(lambda x: re.fullmatch(x["path"], str(request.rel_url)) is not None, self.routes))
        if len(found_routes) > 1:
            raise web.HTTPMultipleChoices(request.rel_url)
        elif len(found_routes) == 1:

            return await found_routes[0]["handler"](request, {k: str(request.rel_url).split("/")[v]
                                                              for k, v in found_routes[0]["params"].items()})
        elif len(found_routes) == 0:
            found_routes_other = list(filter(lambda x: x["path"] == "", self.routes))
            if len(found_routes_other) > 1:
                raise web.HTTPMultipleChoices(request.rel_url)
            elif len(found_routes_other) == 1:
                return await found_routes_other[0]["handler"](request)
            elif len(found_routes_other) == 0:
                return await self.raise_error(request, "404", web.HTTPNotFound)

    def run(self, host="127.0.0.1", port=3000):
        web.run_app(self.app, host=host, port=port)


def send_file(filename):
    with open(filename) as f:
        return f.read()


def static(request, filename):
    static_path = globals()["static_path"] if "static_path" in globals() else "static/"
    try:
        return send_file(static_path+filename)
    except FileNotFoundError:
        return "File Not Found"
