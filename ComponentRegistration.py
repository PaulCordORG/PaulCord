def register_component_handlers(client):
    for attr_name in dir(client):
        attr = getattr(client, attr_name)
        if callable(attr) and hasattr(attr, '_component_handler_info'):
            custom_id = attr._component_handler_info
            client.component_handlers[custom_id] = attr