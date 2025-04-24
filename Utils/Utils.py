import logging
from logging.handlers import RotatingFileHandler
import sys
from rich.logging import RichHandler
from rich.text import Text



def setup_rich_logging(level=logging.INFO, debug : bool = False, LOG_FILENAME="Silly.log") -> None:
        """Setup the logging for the bot and replace the default discord logger with a rich one.
        This will also remove the default discord logger handlers and set the level to WARNING for the `discord.gateway` (for less spam) and `discord.client` loggers.
        
        Args:
            level (_type_, optional): The logging level. Defaults to `logging.INFO`.
            debug (bool, optional): If True, set the logging level to `logging.DEBUG`. Defaults to False.
            LOG_FILENAME (str, optional): The file name of log file. Defaults to "Silly.log".
        """
        handler = RichHandler(rich_tracebacks=True,
                            keywords=["EXECUTE","BOT MISSING PERMISSIONS", "MISSING PERMISSIONS",
                                      "COMMAND ON COOLDOWN", "MISSING REQUIRED ARGUMENT", "COMMAND NOT FOUND", 
                                      "LOADED", "FAILED", "SYNCED"],
                            markup=True)


        root_logger = logging.getLogger()
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)

        file_formatter = logging.Formatter(
            fmt="[{asctime}] [{levelname:<8}] [{filename}:{lineno}] {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{"
        )
        
        original_format = file_formatter.format
        def format(record):
            record.msg = Text.from_markup(str(record.msg)).plain
            return original_format(record)
        file_formatter.format = format
        
        file_handler = RotatingFileHandler(LOG_FILENAME,
                                        maxBytes=10**6,
                                        backupCount=5)
        file_handler.setFormatter(file_formatter)
        
        logging.basicConfig(
            level="DEBUG" if debug else "INFO",
            format="%(message)s",
            datefmt="[%Y-%m-%d %H:%M:%S]",
            handlers=[handler, 
                    file_handler],
            force=True,
        )

        for name in ["discord", "discord.gateway", "discord.client"]:
            logger = logging.getLogger(name)
            logger.handlers = []  
            logger.propagate = False 
            logger.addHandler(handler)
            logger.setLevel(level if name != "discord.gateway" else logging.WARNING)