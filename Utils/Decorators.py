from PaulCord.Utils.CommandRegistration import SlashCommand

class CommandDecorator:
    def __init__(self, client):
        self.client = client
        self.commands = []

    def slash_commands(self, name=None, description=None, options=None, integration_types=False):
        def wrapper(func):
            if not description:
                raise ValueError(f"Description is required for command '{name}'")

            cmd = SlashCommand(
                name=name or func.__name__,
                description=description or func.__doc__,
                options=options or []
            )
            self.client.commands.append({
                "name": cmd.name,
                "description": cmd.description,
                "func": func,
                "options": cmd.options,
                "integration_types": integration_types
            })
            return func
        return wrapper

    def sub_command(self, parent_name, name=None, description=None):
        def wrapper(func):
            parent_command = next((cmd for cmd in self.client.commands if cmd["name"] == parent_name), None)
            if not parent_command:
                raise ValueError(f"No parent command with name '{parent_name}' found")

            if "options" not in parent_command:
                parent_command["options"] = []

            if not description:
                raise ValueError(f"Description is required for subcommand '{name}'")

            sub_cmd = {
                "type": 1,
                "name": name or func.__name__,
                "description": description,
                "func": func
            }

            parent_command["options"].append(sub_cmd)
            return func
        return wrapper

    def sub_command_group(self, parent_name, group_name, description=None):     
        def wrapper(func):
            parent_command = next((cmd for cmd in self.client.commands if cmd["name"] == parent_name), None)
            if not parent_command:
                raise ValueError(f"No parent command with name '{parent_name}' found")

            if "options" not in parent_command:
                parent_command["options"] = []

            if not description:
                raise ValueError(f"Description is required for subcommand group '{group_name}'")

            sub_command_group = {
                "type": 2,
                "name": group_name,
                "description": description,
                "options": [] 
            }

            parent_command["options"].append(sub_command_group)
            return func
        return wrapper

class ComponentHandlerDecorator:
    def __init__(self, client):
        self.client = client
        self.component_handlers = {}

    def component_handler(self, custom_id=None):
        def wrapper(func):
            print(f"Registering component handler for custom_id: {custom_id}")
            self.component_handlers[custom_id] = func
            return func
        return wrapper

