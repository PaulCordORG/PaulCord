class Embed:
    def __init__(self, title=None, description=None, color=None, fields=None, footer=None, thumbnail=None, image=None):
        self.embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": fields or [],
            "footer": footer or {},
            "thumbnail": thumbnail or {},
            "image": image or {}
        }

    def add_field(self, name, value, inline=False):
        field = {"name": name, "value": value, "inline": inline}
        self.embed["fields"].append(field)

    def set_footer(self, text, icon_url=None):
        self.embed["footer"] = {"text": text, "icon_url": icon_url}

    def set_thumbnail(self, url):
        self.embed["thumbnail"] = {"url": url}

    def set_image(self, url):
        self.embed["image"] = {"url": url}

    def to_dict(self):
        return self.embed
