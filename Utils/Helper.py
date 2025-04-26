import inspect
import logging
from typing import Any, List

from discord.ext import commands
from configparser import ConfigParser
from discord import Emoji
import random as rd

logger = logging.getLogger("Silly")


class Emojis_Class:
    """Class to manage all emojis."""

    Filter_words = ["BTN", "ICON"]

    def __init__(self):
        self._emojis = {}
        self._cats: List[Emoji] = []

    def add(self, name: str, emoji: Emoji):
        """Add an emoji to the collection."""
        self._emojis[name] = emoji
        if not any(kw.lower() in name.lower() for kw in self.Filter_words):
            self._cats.append(emoji)

    def get(self, name: str, many: int = 1) -> str:
        """Get emoji by name."""
        emoji = self._emojis.get(name)
        if emoji:
            return (
                f"<{emoji.animated and 'a' or ''}:{emoji.name}:{emoji.id}>{" " if many > 1 else ""}"
                * many
            )
        return ""

    def random(self, many: int = 1, filter_emoji: str = None) -> str:
        """Get a random cat emoji."""

        # Filter cats based on name if filter_emoji is provided
        available_cats = self._cats
        if filter_emoji:
            available_cats = [cat for cat in self._cats if filter_emoji not in cat.name]

        if many > 1:
            text = ""
            for _ in range(many):
                emoji = rd.choice(available_cats)
                text += f"<{emoji.animated and 'a' or ''}:{emoji.name}:{emoji.id}> "
            return text.rstrip()

        emoji = rd.choice(available_cats)
        return f"<{emoji.animated and 'a' or ''}:{emoji.name}:{emoji.id}>"

    async def Init(self, Bot: commands.Bot):
        """Init the emojis."""
        Emojis = await Bot.fetch_application_emojis()
        for Emoji in Emojis:
            self.add(Emoji.name, Emoji)

            if not any(kw.lower() in Emoji.name.lower() for kw in self.Filter_words):
                self._cats.append(Emoji)

    def __getattr__(self, name: str) -> str:
        """Allow direct access to emojis as attributes."""
        return self.get(name)

    def __mul__(self, other: str) -> str:
        return self + " " * other


def get_required_permissions(command: commands.Command) -> List[str]:
    """
    Extracts required permissions from a command's checks (specifically for @has_permissions).
    Returns a list of permission names as strings.
    """
    required_permissions = []

    for check in command.checks:
        # if it's a decorator like @commands.has_permissions
        if hasattr(check, "__name__") and check.__name__ == "predicate":
            try:
                closure_vars = inspect.getclosurevars(check)
                perms = closure_vars.nonlocals.get("perms")
                if isinstance(perms, dict):
                    required_permissions.extend(
                        [perm for perm, value in perms.items() if value]
                    )
            except Exception as e:
                logger.warning(
                    f"Error getting required permissions for command {command.name}: {e}"
                )

    return required_permissions


INI: ConfigParser = ConfigParser()
INI.read("Settings.ini")
Emojis = Emojis_Class()
