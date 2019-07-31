from lite import Lite, LiteErrorHandler


def hello(request):
    return {"hello": "world"}


def param(request, prm):
    return {"prm": prm}


def handler404(request, error, msg):
    return {"error": [error, msg]}


handler = LiteErrorHandler([
    {
        "error": 404,
        "handler": handler404
    }
]).middlewares

Lite([
    {
        "path": "/",
        "handler": hello
    },
    {
        "path": "/param/{prm}",
        "handler": param
    }
], handler).run()

