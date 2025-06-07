indicator_registry = {}

def register_indicator(name):
    def wrapper(fn):
        indicator_registry[name] = fn
        return fn
    return wrapper
