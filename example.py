from lite import Lite


def hello(request):
    return {"hello": "world"}


def func_with_arg(request, arg):
    return {"arg": arg}


Lite([
    {
        "path": "/",
        "handler": hello
    },
    {
        "path": "/arg/{str:arg}",
        "handler": func_with_arg
    },
    {
        "path": "404",
        "handler": lambda req: "Page Not Found :("
    }
]).run()

