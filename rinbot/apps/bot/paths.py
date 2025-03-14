from strenum import StrEnum

from .helpers import get_os_path


class Path(StrEnum):
    """
    A list of paths to the files and directories in the bot
    """

    ASSETS = get_os_path("assets")
    CONFIG = get_os_path("config/rinbot.yml")
    EXTENSIONS = get_os_path("extensions")
    LOCALE = get_os_path("locale")
    LOG_LATEST = get_os_path("/var/lib/rinbot/logs/latest.log", from_root=True)
    LOG_HISTORY = get_os_path("/var/lib/rinbot/logs/history", from_root=True)
    LOG_TRACEBACKS = get_os_path("/var/lib/rinbot/logs/tracebacks", from_root=True)

    @classmethod
    def list_paths(cls) -> list[str]:
        """
        Returns a list of all the paths in the Paths enum
        """
        
        return [path.value for path in cls]
