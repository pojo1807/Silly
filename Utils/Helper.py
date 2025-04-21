import inspect
from typing import Any, List

from discord.ext import commands
from configparser import ConfigParser
from discord import Emoji
import random as rd

class Emojis_Class:
    """Class to manage all emojis."""
    Filter_words = ["BTN", "ICON"]
    
    def __init__(self):
        self._emojis = {}
        self._cats = []
        
    def add(self, name: str, emoji: Emoji):
        """Add an emoji to the collection."""
        self._emojis[name] = emoji
        if not any(kw.lower() in name.lower() for kw in self.Filter_words):
            self._cats.append(emoji)
        
    def get(self, name: str, many: int = 1) -> str:
        """Get emoji by name."""
        emoji = self._emojis.get(name)
        if emoji:
            return f"<{emoji.animated and 'a' or ''}:{emoji.name}:{emoji.id}>{" " if many > 1 else ""}" * many
        return ""
        
    def random(self, many: int = 1) -> str:
        """Get a random cat emoji."""
        if not self._cats:
            return ""
        emoji = rd.choice(self._cats)
        return f"<{emoji.animated and 'a' or ''}:{emoji.name}:{emoji.id}>{" " if many > 1 else ""}" * many
    
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
        # Nếu là decorator kiểu @commands.has_permissions
        if hasattr(check, "__name__") and check.__name__ == "predicate":
            try:
                closure_vars = inspect.getclosurevars(check)
                perms = closure_vars.nonlocals.get("perms")
                if isinstance(perms, dict):
                    required_permissions.extend([perm for perm, value in perms.items() if value])
            except Exception as e:
                # Bạn có thể log nếu muốn
                pass  # hoặc self.Logger.warning(...)
    
    return required_permissions


INI: ConfigParser = ConfigParser()
INI.read("Settings.ini")
Emojis = Emojis_Class()
