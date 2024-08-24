class CommandDecorator:
    def __init__(self, client):
        self.client = client
        self.commands = []

    def slash_commands(self, name=None, description=None):
        def wrapper(func):
            cmd = {
                "name": name or func.__name__,
                "description": description or func.__doc__,
                "func": func
            }
            self.client.commands.append(cmd)
            return func
        return wrapper

class ComponentHandlerDecorator:
    def __init__(self, client):
        self.client = client
        self.component_handlers = {}

    def component_handler(self, custom_id=None):
        def wrapper(func):
            self.component_handlers[custom_id] = func
            return func
        return wrapper
