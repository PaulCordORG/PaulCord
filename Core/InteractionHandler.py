class InteractionHandler:
    def __init__(self, client):
        self.client = client


    async def send_interaction_response(self, interaction_id, interaction_token, message=None, embed=None, ephemeral=False, components=None):
        await self.client.api_helper.send_interaction_response(interaction_id, interaction_token, message, embed, ephemeral, components)

    async def handle_command(self, interaction):
        command_name = interaction['data']['name']
        command = next((cmd for cmd in self.client.commands if cmd['name'] == command_name), None)
        if command:
            await command['func'](self.client, interaction)
            print(f"Received slash command: {command_name}")
        else:
            print(f"Unknown command: {command_name}")

    async def handle_component(self, interaction):
        custom_id = interaction['data'].get('custom_id', '')
        handler = self.client.component_handlers.get(custom_id)
        if handler:
            await handler(self.client, interaction)
        else:
            print(f"No handler found for component with custom_id: {custom_id}")

    async def handle_interaction(self, interaction):
        print(f"Handling interaction: {interaction}")
        interaction_type = interaction.get('type')

        if not interaction_type:
            print("Interaction type missing in payload.")
            return

        if interaction_type == 2:
            command_name = interaction['data']['name']
            print(f"Received slash command: {command_name}")
            command = next((cmd for cmd in self.client.commands if cmd['name'] == command_name), None)

            if command:
                try:
                    print(f"Executing command: {command_name}")
                    result_message = await command['func'](self.client, interaction)
                    if result_message:
                        await self.client.api_helper.send_interaction_response(
                            interaction["id"],
                            interaction["token"],
                            message=result_message
                        )
                    else:
                        print(f"No response message for command {command_name}, skipping send.")
                except Exception as e:
                    print(f"Error while executing command {command_name}: {e}")
                    await self.client.api_helper.send_interaction_response(
                        interaction["id"],
                        interaction["token"],
                        message="An error occurred while executing the command."
                    )
            else:
                print(f"Unknown command: {command_name}")
                await self.client.api_helper.send_interaction_response(
                    interaction["id"], interaction["token"], message="Unknown command"
                )

        elif interaction_type == 3:
            custom_id = interaction['data'].get('custom_id', '')
            handler = self.client.component_handlers.get(custom_id)
            if handler:
                try:
                    await handler(self.client, interaction)
                except Exception as e:
                    print(f"Error while handling component {custom_id}: {e}")
                    await self.client.api_helper.send_interaction_response(
                        interaction["id"], interaction["token"], message="An error occurred while handling the component."
                    )
            else:
                print(f"No handler found for component with custom_id: {custom_id}")
                await self.client.api_helper.send_interaction_response(
                    interaction["id"], interaction["token"], message="No handler for this component."
                )

        elif interaction_type == 5:
            custom_id = interaction['data'].get('custom_id', '')
            try:
                await self.handle_modal(interaction, custom_id)
            except Exception as e:
                print(f"Error while handling modal {custom_id}: {e}")
                await self.client.api_helper.send_interaction_response(
                    interaction["id"], interaction["token"], message="An error occurred while handling the modal."
                )

        else:
            print(f"Unknown interaction type: {interaction_type}")
            await self.client.api_helper.send_interaction_response(
                interaction["id"], interaction["token"], message="Unknown interaction type"
            )
