from typing import Any
import logging

from discord.ext import commands
from discord.utils import get
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


class Images_Class:
    """Class to manage all images."""
    def __init__(self):
        self._images = []
        
    def add(self, name: str, image: str):
        """Add an image to the collection."""
        self._images.append(image)


Emojis = Emojis_Class()
