import discord
from discord import app_commands
from discord.ext import commands

from servercontrol.config import ManagerConfig

from .commands import echo


def register_handlers_discord(bot: commands.Bot, config: ManagerConfig):
    """Registra los slash commands y eventos para el bot de Discord."""

    @bot.tree.command(
        name="echo",
        description="Repite el texto que envíes.",
        guild=discord.Object(id=config.discord_config.guild_id) if config.discord_config.guild_id else None
    )
    @app_commands.describe(text="El texto que quieres que repita.")
    async def echo_command(interaction: discord.Interaction, text: str):
        await echo(interaction, text)

    @bot.event
    async def on_ready():
        print(f"Bot de Discord conectado como {bot.user}")
        try:
            guild = discord.Object(id=config.discord_config.guild_id) if config.discord_config.guild_id else None
            synced = await bot.tree.sync(guild=guild)
            print(f"Sincronizados {len(synced)} comandos.")
        except Exception as e:
            print(f"Error al sincronizar comandos: {e}")