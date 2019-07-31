from aiohttp import web
import json


class Lite:
    def __init__(self, routes, error_handlers=()):
        self.routes = routes
        self.app = web.Application(middlewares=[*error_handlers])

        for route in routes:
            if "methods" not in route:
                route["methods"] = ["get"]
            route["methods"] = frozenset(route["methods"])

            if route["path"] == "*":
                def error_wrapper(func):
                    @web.middleware
                    async def error_middleware(request, handler):
                        try:
                            response = await handler(request)
                            if response.status != 404:
                                return response
                        except web.HTTPException:
                            return await self.wrapper(func)(request)
                    return error_middleware
                self.app.middlewares.append(error_wrapper(route["handler"]))
            else:
                route["handler"] = self.wrapper(route["handler"])
                for method in route["methods"]:
                    {
                        "get": lambda: self.app.router.add_get(route["path"], route["handler"]),
                        "post": lambda: self.app.router.add_post(route["path"], route["handler"]),
                        "put": lambda: self.app.router.add_put(route["path"], route["handler"]),
                        "delete": lambda: self.app.router.add_delete(route["path"], route["handler"])
                    }.setdefault(method.lower(), lambda: self.app.router.add_options(route["path"], route["handler"]))()

    @staticmethod
    def wrapper(func):
        async def function_wrapper(request):
            req = {
                "original": request,
                "params": dict(request.match_info),
                "query": dict(request.rel_url.query),
                "method": request.method,
                "url": request.url,
                "headers": dict(request.headers),
                "cookies": dict(request.cookies),
            }

            response = func(req, **req["params"])
            return {
                dict: web.Response(text=json.dumps(response), content_type="application/json"),
                str: web.Response(text=str(response), content_type="text/html")
            }.setdefault(type(response), web.Response(text=str(response), content_type="text/plain"))
        return function_wrapper

    def run(self, host="127.0.0.1", port=3000):
        web.run_app(self.app, host=host, port=port)


class LiteErrorHandler:
    def __init__(self, handlers):
        self.handlers = handlers
        self._middlewares = []
        for handler in handlers:
            self._middlewares.append(self.error_wrapper(handler["handler"], handler["error"]))

    @staticmethod
    async def wrapper(func, request, error, msg):
        req = {
            "original": request,
            "params": dict(request.match_info),
            "query": dict(request.rel_url.query),
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "cookies": dict(request.cookies),
        }

        response = func(req, error, msg)
        return {
            dict: web.Response(text=json.dumps(response), content_type="application/json"),
            str: web.Response(text=str(response), content_type="text/html")
        }.setdefault(type(response), web.Response(text=str(response), content_type="text/plain"))

    def error_wrapper(self, func, code):
        @web.middleware
        async def error_middleware(request, handler):
            try:
                response = await handler(request)
                if response.status != code:
                    return response
                status = response.status
                message = response.message
            except web.HTTPException as ex:
                status = ex.status
                message = ex.reason
                if status != code:
                    raise
            return await self.wrapper(func, request, status, message)
        return error_middleware

    @property
    def middlewares(self):
        return self._middlewares


def send_file(filename):
    with open(filename) as f:
        return f.read()


def static(request, filename):
    static_path = globals()["static_path"] if "static_path" in globals() else "static/"
    try:
        return send_file(static_path+filename)
    except FileNotFoundError:
        return "File Not Found"
