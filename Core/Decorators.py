from PaulCord.Core.CommandRegistration import SlashCommand

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
    
    def CheckPermission(self, **permissions):
        def wrapper(func):
            async def wrapped_func(client, interaction, *args, **kwargs):
                member_permissions = interaction['member']['permissions']
                
                permissions_to_check = {
                    "create_instant_invite": 1 << 0,
                    "kick_members": 1 << 1,
                    "ban_members": 1 << 2,
                    "administrator": 1 << 3,
                    "manage_channels": 1 << 4,
                    "manage_guild": 1 << 5,
                    "add_reactions": 1 << 6,
                    "view_audit_log": 1 << 7,
                    "priority_speaker": 1 << 8,
                    "stream": 1 << 9,
                    "view_channel": 1 << 10,
                    "send_messages": 1 << 11,
                    "send_tts_messages": 1 << 12,
                    "manage_messages": 1 << 13,
                    "embed_links": 1 << 14,
                    "attach_files": 1 << 15,
                    "read_message_history": 1 << 16,
                    "mention_everyone": 1 << 17,
                    "use_external_emojis": 1 << 18,
                    "view_guild_insights": 1 << 19,
                    "connect": 1 << 20,
                    "speak": 1 << 21,
                    "mute_members": 1 << 22,
                    "deafen_members": 1 << 23,
                    "move_members": 1 << 24,
                    "use_vad": 1 << 25,
                    "change_nickname": 1 << 26,
                    "manage_nicknames": 1 << 27,
                    "manage_roles": 1 << 28,
                    "manage_webhooks": 1 << 29,
                    "manage_guild_expressions": 1 << 30,
                    "use_application_commands": 1 << 31,
                    "request_to_speak": 1 << 32,
                    "manage_events": 1 << 33,
                    "manage_threads": 1 << 34,
                    "create_public_threads": 1 << 35,
                    "create_private_threads": 1 << 36,
                    "use_external_stickers": 1 << 37,
                    "send_messages_in_threads": 1 << 38,
                    "use_embedded_activities": 1 << 39,
                }

                for permission, value in permissions.items():
                    if permissions_to_check.get(permission) and not (int(member_permissions) & permissions_to_check[permission]):
                        client.send_interaction_response(
                            interaction['id'],
                            interaction['token'],
                            message=f"Missing required permission: {permission.replace('_', ' ').title()}",
                            ephemeral=True
                        )
                        return

                return await func(client, interaction, *args, **kwargs)

            return wrapped_func
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

