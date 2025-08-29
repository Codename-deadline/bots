class InvalidChatException(Exception):
    """Invalid chat type for a command"""

    is_db: bool

    def __init__(self, is_dm: bool = False):
        self.is_dm = is_dm
