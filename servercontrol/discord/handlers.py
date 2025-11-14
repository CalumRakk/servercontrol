import discord
from discord import app_commands
from discord.ext import commands

from servercontrol.config import ManagerConfig

from .commands import echo, start_minecraft_server, stop_minecraft_server


def register_handlers_discord(bot: commands.Bot, config: ManagerConfig):
    """Registra los slash commands y eventos para el bot de Discord."""

    # Comando echo
    @bot.tree.command(
        name="echo",
        description="Repite el texto que envíes.",
        guild=(
            discord.Object(id=config.discord_config.guild_id)
            if config.discord_config.guild_id
            else None
        ),
    )
    @app_commands.describe(text="El texto que quieres que repita.")
    async def echo_command(interaction: discord.Interaction, text: str):
        await echo(interaction, text)

    # Comando iniciar servidor
    @bot.tree.command(
        name="server_start",
        description="Inicia el servidor de Minecraft si está apagado.",
        guild=(
            discord.Object(id=config.discord_config.guild_id)
            if config.discord_config.guild_id
            else None
        ),
    )
    @app_commands.checks.has_role("Admin")
    async def server_start(interaction: discord.Interaction):
        await start_minecraft_server(interaction, config.minecraft_config)

    @server_start.error
    async def server_start_error(
        interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(
                "No tienes permiso para usar este comando.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Ocurrió un error: {error}", ephemeral=True
            )

    # Comando detener servidor
    @bot.tree.command(
        name="server_stop",
        description="Detiene el servidor de Minecraft si estaba corriendo.",
        guild=(
            discord.Object(id=config.discord_config.guild_id)
            if config.discord_config.guild_id
            else None
        ),
    )
    @app_commands.checks.has_role("Admin")
    async def server_stop(interaction: discord.Interaction):
        await stop_minecraft_server(interaction, config.minecraft_config)

    @server_stop.error
    async def server_stop_error(
        interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(
                "No tienes permiso para usar este comando.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Ocurrió un error: {error}", ephemeral=True
            )

    @bot.event
    async def on_ready():
        print(f"Bot de Discord conectado como {bot.user}")
        try:
            guild = (
                discord.Object(id=config.discord_config.guild_id)
                if config.discord_config.guild_id
                else None
            )
            synced = await bot.tree.sync(guild=guild)
            print(f"Sincronizados {len(synced)} comandos.")
        except Exception as e:
            print(f"Error al sincronizar comandos: {e}")
