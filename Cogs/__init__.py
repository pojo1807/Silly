from discord.ext import commands
from discord import app_commands
from typing import List, Dict, Any, Callable, Type, Optional, Union
import logging
import asyncio

logger = logging.getLogger(__name__)


class BetterCommand:
    def __init__(
        self,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,
        brief: Optional[str] = None,
        help: Optional[str] = None,
        usage: Optional[str] = None,
        hidden: bool = False,
        enabled: bool = True,
        ignore_extra: bool = True,
        extras: Optional[Dict[Any, Any]] = None,
        rest_is_raw: bool = False,
        cooldown_after_parsing: bool = False,
        cls: Optional[Type[commands.Command]] = None,
        debrise: Optional[str] = None,
        describe: Optional[Dict[str, str]] = None,
        dm_permission: bool = False,
    ) -> None:
        """Initialize a BetterCommand instance.

        Args:
            name (Optional[str]): The name of the command.
            aliases (Optional[List[str]]): Alternative names for the command.
            description (Optional[str]): A brief description of what the command does.
            brief (Optional[str]): A short description of the command.
            help (Optional[str]): A detailed help message for the command.
            usage (Optional[str]): Usage examples for the command.
            hidden (bool): Whether the command should be hidden from help.
            enabled (bool): Whether the command is enabled.
            ignore_extra (bool): Whether to ignore extra arguments.
            extras (Optional[Dict[Any, Any]]): Additional command attributes.
            rest_is_raw (bool): Whether to pass the rest of the arguments as raw.
            cooldown_after_parsing (bool): Whether to apply cooldown after parsing.
            cls (Optional[Type[commands.Command]]): Custom command class to use.
            debrise (Optional[str]): Additional brief description.
            describe (Optional[Dict[str, str]]): Parameter descriptions for slash commands.
            dm_permission (bool): Whether the command can be used in DMs.
        """
        self.name = name
        self.kwargs = {
            "aliases": aliases,
            "description": description,
            "brief": brief,
            "help": help,
            "usage": usage,
            "hidden": hidden,
            "enabled": enabled,
            "ignore_extra": ignore_extra,
            "extras": extras or {},
            "rest_is_raw": rest_is_raw,
            "cooldown_after_parsing": cooldown_after_parsing,
            "cls": cls,
            "dm_permission": dm_permission,
        }
        self.kwargs = {
            k: v for k, v in self.kwargs.items() if v is not None
        }  # Filter out None values

        if debrise:
            self.kwargs["extras"]["debrise"] = debrise
        self.describe = describe or {}

    def __call__(self, func: Callable) -> commands.HybridCommand:
        """Create a hybrid command from the decorated function.

        Args:
            func (Callable): The function to decorate.

        Returns:
            commands.HybridCommand: The created hybrid command.

        Raises:
            ValueError: If the function is not a coroutine.
        """
        if not asyncio.iscoroutinefunction(func):
            raise ValueError(f"Function {func.__name__} must be a coroutine")

        try:
            # Create a hybrid command with the provided name and kwargs
            cmd = commands.hybrid_command(name=self.name, **self.kwargs)(func)

            # add describe for slash command if needed
            if self.describe:
                try:
                    app_commands.describe(**self.describe)(cmd)
                except Exception as e:
                    logger.warning(
                        f"Failed to apply app_commands.describe to {func.__name__}: {e}"
                    )

            return cmd
        except Exception as e:
            logger.error(f"Failed to create hybrid command for {func.__name__}: {e}")
            raise


def HelpFormat(
    Command: str,
    Required: Dict[str, Union[str, Dict[str, str]]] = {},
    Optional: Optional[Dict[str, Union[str, Dict[str, str]]]] = None,
) -> str:
    """Format command usage help with ANSI colors and simpler structure.

    Args:
        Command (str): The command name.
        Required (dict): Dict where values are either str or nested dicts.
        Optional (dict): Same as Required, but for optional args.

    Returns:
        str: Formatted help string.
    """

    def format_section(
        params: Dict[str, Union[str, Dict[str, str]]], color_code: str, bracket: str
    ):
        lines = []
        usage_parts = []
        for key, val in params.items():
            usage_parts.append(
                f"\x1b[2;{color_code}m{bracket[0]}{key}{bracket[1]}\x1b[0m"
            )
            if isinstance(val, str):
                lines.append(f"-# **{key}**: {val}")
            elif isinstance(val, dict):
                lines.append(f"-# __**{key}**__: {val.get('', '...')}")
                for sub_key, sub_desc in val.items():
                    if sub_key != "":
                        lines.append(f"> -# **{sub_key}**: {sub_desc}")
        return usage_parts, lines

    usage_required, desc_required = format_section(Required, "31", "<>")
    usage_optional, desc_optional = format_section(Optional or {}, "32", "[]")

    usage_line = f"{Command} " + " ".join(usage_required + usage_optional)
    description = (
        f'-# **Parameter description:**\n{"\n".join(desc_required + desc_optional)}'
    )

    return f"""{description}
```ansi
\x1b[2;31m<> \x1b[0mis \x1b[2;31mRequired\x1b[0m
\x1b[2;32m[] \x1b[0mis \x1b[2;32mOptional\x1b[0m

{usage_line}
```"""
