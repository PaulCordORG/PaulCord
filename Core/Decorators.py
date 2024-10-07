from ..Core.CommandRegistration import SlashCommand
import asyncio

class CommandDecorator:
    def __init__(self, client):
        self.client = client
        self.commands = []

    def slash_commands(self, name=None, description=None, options=None, integration_types=False):
        def wrapper(func):
            if not description:
                raise ValueError(f"Description is required for command '{name}'")

            cmd = {
                "name": name or func.__name__,
                "description": description or func.__doc__,
                "func": func,
                "options": options or [],
                "integration_types": integration_types
            }

            self.client.commands.append(cmd)
            print(f"Registered slash command: {cmd['name']} - {cmd['description']}")

            return func
        return wrapper

    async def reload_command(self, command_name):

        command = next((cmd for cmd in self.client.commands if cmd['name'] == command_name), None)
        
        if not command:
            print(f"Command '{command_name}' not found.")
            return f"Command '{command_name}' not found."

        try:
            await self.client.command_registration.sync_commands()
            print(f"Command '{command_name}' reloaded successfully.")
            return f"Command '{command_name}' reloaded successfully."
        except Exception as e:
            print(f"Failed to reload command '{command_name}': {e}")
            return f"Failed to reload command '{command_name}': {e}"


    def permissions(self, **permissions):
        def wrapper(func):
            async def wrapped_func(client, interaction, *args, **kwargs):
                print(f"Interaction data for debugging: {interaction}")

                if 'member' not in interaction or 'permissions' not in interaction['member']:
                    await client.api_helper.send_interaction_response(
                        interaction['id'],
                        interaction['token'],
                        message="Unable to verify permissions.",
                        ephemeral=True
                    )
                    return

                member_permissions = int(interaction['member']['permissions'])
                print(f"Converted permissions value: {member_permissions}")

                missing_permissions = []

                for permission, required in permissions.items():
                    required_bit = 1 << required
                    print(f"Checking permission '{permission}' ({required_bit}) against member permissions: {member_permissions}")
                    if not (member_permissions & required_bit):
                        missing_permissions.append(permission)

                if missing_permissions:
                    await client.api_helper.send_interaction_response(
                        interaction['id'],
                        interaction['token'],
                        message=f"Missing required permissions: {', '.join(missing_permissions)}",
                        ephemeral=True
                    )
                    return

                return await func(client, interaction, *args, **kwargs)

            return wrapped_func
        return wrapper

    def member(self, id=None):
        def wrapper(func):
            async def wrapped_func(client, interaction, *args, **kwargs):
                user_id = str(interaction['member']['user']['id'])
                allowed_ids = [str(id)] if isinstance(id, str) else [str(uid) for uid in id]

                if user_id not in allowed_ids:
                    await client.api_helper.send_interaction_response(
                        interaction['id'],
                        interaction['token'],
                        message="You do not have permission to use this command.",
                        ephemeral=True
                    )
                    return
                return await func(client, interaction, *args, **kwargs)
            return wrapped_func
        return wrapper

    def role(self, id=None):
        def wrapper(func):
            async def wrapped_func(client, interaction, *args, **kwargs):
                if 'roles' not in interaction['member']:
                    await client.api_helper.send_interaction_response(
                        interaction['id'],
                        interaction['token'],
                        message="Unable to verify roles.",
                        ephemeral=True
                    )
                    return

                user_roles = set(str(role) for role in interaction['member']['roles'])
                allowed_roles = {str(id)} if isinstance(id, str) else {str(rid) for rid in id}

                if not user_roles.intersection(allowed_roles):
                    await client.api_helper.send_interaction_response(
                        interaction['id'],
                        interaction['token'],
                        message="You do not have the required role to use this command.",
                        ephemeral=True
                    )
                    return
                return await func(client, interaction, *args, **kwargs)
            return wrapped_func
        return wrapper

    def dev(self, id=None):
        def wrapper(func):
            async def wrapped_func(client, interaction, *args, **kwargs):
                user_id = str(interaction['member']['user']['id'])
                dev_ids = [str(id)] if isinstance(id, str) else [str(dev_id) for dev_id in id]

                if user_id not in dev_ids:
                    await client.api_helper.send_interaction_response(
                        interaction['id'],
                        interaction['token'],
                        message="This command is restricted to bot developers only.",
                        ephemeral=True
                    )
                    return
                return await func(client, interaction, *args, **kwargs)
            return wrapped_func
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
