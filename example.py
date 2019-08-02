from lite import Lite


def hello(request):
    return {"hello": "world"}


Lite([
    {
        "path": "/",
        "handler": hello
    }
]).run()

