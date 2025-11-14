import subprocess
from pathlib import Path
from typing import Sequence, cast

import discord

from servercontrol.config import MinecraftConfig

from .guild_config import GuildConfigManager

# --- Utilidades ---


def exists_tmux_session(session_name: str) -> bool:
    """Comprueba si una sesión de tmux con el nombre dado existe. Devuelve True si existe, False si no."""
    check_process = subprocess.run(["tmux", "has-session", "-t", session_name])
    return check_process.returncode == 0


# --- Comandos ---


async def echo(interaction: discord.Interaction, text: str):
    """
    Función de lógica para el comando echo.
    Responde a la interacción con el mismo texto proporcionado.
    """
    # El `ephemeral=True` aquí hace que el mensaje "pensando..." solo lo vea el usuario.
    await interaction.response.defer(ephemeral=True)

    # Enviamos la respuesta final usando followup.send()
    await interaction.followup.send(f"Dijiste: {text}")


async def start_minecraft_server(
    interaction: discord.Interaction, config: MinecraftConfig
):
    """
    Inicia el servidor de Minecraft en una sesión 'tmux' si no está ya corriendo.
    """
    await interaction.response.defer(ephemeral=True)

    session_name = config.terminal_session_name
    if exists_tmux_session(session_name):
        await interaction.followup.send(
            f"El servidor de Minecraft ya está en ejecución en la sesión de tmux `{session_name}`."
        )
        return

    # 2. Si no existe, iniciarlo
    server_path = Path(config.server_path)
    start_script = server_path / "start.sh"

    if not start_script.exists():
        await interaction.followup.send(
            f"**Error:** No se encontró el script `start.sh` en la ruta `{server_path}`."
        )
        return

    try:
        subprocess.Popen(
            ["tmux", "new-session", "-s", session_name, "-d", str(start_script)]
        )
        await interaction.followup.send(
            f"¡Iniciando el servidor de Minecraft en la sesión de tmux `{session_name}`! Dale uno o dos minutos para que arranque."
        )

    except Exception as e:
        await interaction.followup.send(
            f"**Error inesperado al iniciar el servidor:**\n```\n{e}\n```"
        )


async def stop_minecraft_server(
    interaction: discord.Interaction, config: MinecraftConfig
):
    """
    Envía el comando 'stop' a la sesión tmux del servidor de Minecraft.
    """
    await interaction.response.defer(ephemeral=True)
    session_name = config.terminal_session_name

    if exists_tmux_session(session_name) is False:
        await interaction.followup.send(
            f"El servidor de Minecraft no está en ejecución. No se encontró la sesión de tmux `{session_name}`."
        )
        return

    try:
        # Enviamos el comando 'stop' y luego la tecla Enter (C-m)
        subprocess.run(
            [
                "tmux",
                "send-keys",
                "-t",
                session_name,
                "stop",
                "C-m",
            ]
        )
        await interaction.followup.send(
            f"Comando de apagado enviado al servidor. La sesión de tmux `{session_name}` se cerrará en breve."
        )

    except Exception as e:
        await interaction.followup.send(
            f"**Error inesperado al intentar detener el servidor:**\n```\n{e}\n```"
        )


async def setup_bot_role(
    interaction: discord.Interaction, rolename: str, config_manager: GuildConfigManager
):
    """
    Verifica si el rol de admin existe y lo crea si es necesario.
    """
    await interaction.response.defer(ephemeral=True)

    # 1. Verificar si el USUARIO que ejecuta el comando es un admin del servidor
    guild_permissions = cast(
        discord.Permissions, getattr(interaction.user, "guild_permissions", None)
    )
    if guild_permissions is None or not guild_permissions.manage_roles:
        await interaction.followup.send(
            "Debes tener el permiso de 'Gestionar Roles' para ejecutar este comando.",
            ephemeral=True,
        )
        return

    # 2. Verificar si el BOT tiene permiso para gestionar roles
    bot_member = getattr(interaction.guild, "me", None)
    if bot_member is None or not bot_member.guild_permissions.manage_roles:
        await interaction.followup.send(
            "**¡Error crítico!** No tengo el permiso de 'Gestionar Roles'.\n"
            "Por favor, re-invítame con los permisos correctos o asígname un rol que los tenga.",
            ephemeral=True,
        )
        return

    # 3. Verificar si el rol ya existe
    roles: Sequence[discord.Role] = getattr(interaction.guild, "roles", [])
    existing_role = discord.utils.get(roles, name=rolename)
    if existing_role:
        await interaction.followup.send(
            f"El rol '{rolename}' ya existe. ¡Todo listo!", ephemeral=True
        )
        return

    # 4. Si no existe, crearlo
    try:
        new_role = await interaction.guild.create_role(  # type: ignore
            name=rolename,
            reason=f"Rol requerido por {bot_member.display_name} para la administración.",
        )
        config_manager.set_admin_role(interaction.guild.id, rolename)  # type: ignore
        await interaction.followup.send(
            f"Rol '{new_role.name}' creado con éxito. "
            "Ahora puedes usar los comandos restringidos a este rol.",
            ephemeral=True,
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "No pude crear el rol. Asegúrate de que mi rol esté en una posición alta en la jerarquía de roles.",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.followup.send(
            f"Ocurrió un error inesperado al crear el rol: {e}", ephemeral=True
        )
