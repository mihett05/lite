from light import Light


def hello(request):
    return {"hello": "world"}


Light([
    {
        "path": "/",
        "handler": hello
    }
])
