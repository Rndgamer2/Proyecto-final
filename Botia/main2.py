import discord
from discord.ext import commands
import classifier
import database
import os
import uuid
from dotenv import load_dotenv

# Cargar claves del archivo .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

print(f"DISCORD_TOKEN: {DISCORD_TOKEN}")
print(f"OPENROUTER_API_KEY: {OPENROUTER_API_KEY}")
