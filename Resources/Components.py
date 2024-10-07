class Button:
    def __init__(self, label, custom_id, style=1):
        self.type = 2 
        self.label = label
        self.custom_id = custom_id
        self.style = style

    def to_dict(self):
        return {
            "type": self.type,
            "label": self.label,
            "style": self.style,
            "custom_id": self.custom_id
        }

class SelectMenu:
    def __init__(self, custom_id, options, placeholder="Choose an option"):
        self.type = 3
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder

    def to_dict(self):
        return {
            "type": self.type,
            "custom_id": self.custom_id,
            "options": self.options,
            "placeholder": self.placeholder
        }

class Modal:
    def __init__(self, title, custom_id, components=None):
        self.type = 9
        self.title = title
        self.custom_id = custom_id
        self.components = components or []

    def add_component(self, component):
        self.components.append(component)

    def to_dict(self):
        return {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": [component.to_dict() for component in self.components]
        }
    
class ActionRow:
    def __init__(self, components=None):
        self.type = 1   
        self.components = components or []

    def add_component(self, component):
        self.components.append(component)

    def to_dict(self):
        return {
            "type": self.type,
            "components": [component.to_dict() for component in self.components]
        }
