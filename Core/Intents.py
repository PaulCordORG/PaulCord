class Intents:
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21
    GUILD_MESSAGE_POLLS = 1 << 24
    DIRECT_MESSAGE_POLLS = 1 << 25

    ALL = (
        GUILDS
        | GUILD_MEMBERS
        | GUILD_MODERATION
        | GUILD_EMOJIS_AND_STICKERS
        | GUILD_INTEGRATIONS
        | GUILD_WEBHOOKS
        | GUILD_INVITES
        | GUILD_VOICE_STATES
        | GUILD_PRESENCES
        | GUILD_MESSAGES
        | GUILD_MESSAGE_REACTIONS
        | GUILD_MESSAGE_TYPING
        | DIRECT_MESSAGES
        | DIRECT_MESSAGE_REACTIONS
        | DIRECT_MESSAGE_TYPING
        | MESSAGE_CONTENT
        | GUILD_SCHEDULED_EVENTS
        | AUTO_MODERATION_CONFIGURATION
        | AUTO_MODERATION_EXECUTION
        | GUILD_MESSAGE_POLLS
        | DIRECT_MESSAGE_POLLS
    )

    DEFAULT = (
        GUILDS
        | GUILD_MEMBERS
        | GUILD_MESSAGES
        | GUILD_MESSAGE_REACTIONS
        | GUILD_MESSAGE_TYPING
    )

    DEFAULT_FLAGS = {
        'DEFAULT': DEFAULT,
        'ALL': ALL,
    }

    def __int__(self):
        return self.value

    def __init__(self, *intents):
        self.value = self.parse_intents(*intents)

    def parse_intents(self, *intents):
        result = 0
        for intent in intents:
            if isinstance(intent, str):
                result |= self.DEFAULT_FLAGS.get(intent.upper(), 0)
            elif isinstance(intent, int):
                result |= intent
        return result

    def has(self, intent):
        return (self.value & intent) == intent

    def __or__(self, other):
        return Intents(self.value | other.value)

    def __and__(self, other):
        return Intents(self.value & other.value)

    def __repr__(self):
        return f"<Intents value={self.value}>"

    @classmethod
    def none(cls):
        return cls(0)

    @classmethod
    def all(cls):
        return cls(cls.ALL)

    @classmethod
    def default(cls):
        return cls(cls.DEFAULT)

    @classmethod
    def custom(cls, *intents):
        return cls(*intents)

    @staticmethod
    def get_intent_value(*intents):
        intent_value = 0
        for intent in intents:
            intent_value |= intent
        return intent_value
