import subprocess
from pathlib import Path

import discord

from servercontrol.config import MinecraftConfig


async def echo(interaction: discord.Interaction, text: str):
    """
    Función de lógica para el comando echo.
    Responde a la interacción con el mismo texto proporcionado.
    """
    # El `ephemeral=True` aquí hace que el mensaje "pensando..." solo lo vea el usuario.
    await interaction.response.defer(ephemeral=True)

    # Enviamos la respuesta final usando followup.send()
    await interaction.followup.send(f"Dijiste: {text}")


def exists_tmux_session(session_name: str) -> bool:
    """Comprueba si una sesión de tmux con el nombre dado existe. Devuelve True si existe, False si no."""
    check_process = subprocess.run(["tmux", "has-session", "-t", session_name])
    return check_process.returncode == 0


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

    check_process = subprocess.run(["tmux", "has-session", "-t", session_name])
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
