def dev_only(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) != "DEV":
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def non_production(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) not in ["DEV", "BETA"]:
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def prod_only(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) != "PROD":
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner
