from lite import Lite


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
        "path": "/param/{str:prm}",
        "handler": param
    }
]).run()

