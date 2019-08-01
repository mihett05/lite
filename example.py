from lite import Lite, LiteErrorHandler


def hello(request):
    return {"hello": "world"}


def param(request, prm):
    return {"prm": prm}


Lite([
    {
        "path": "/",
        "handler": hello
    },
    {
        "path": "/param/{prm}",
        "handler": param
    }
]).run()

