class ChannelNameError(Exception):
    """Throw if channel name could not be added to channel table."""


class SessionNameNotFound(Exception):
    """Throw if session name not found."""


class HostNotSet(Exception):
    """Throw if host credential values are not set."""


class DatabaseError(Exception):
    """Throw when unexpected database error is raised."""