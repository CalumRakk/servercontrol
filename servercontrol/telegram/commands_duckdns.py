import requests


def update_duckdns(message, domain: str, token: str, ip: str | None) -> bool:
    """Actualiza la IP en DuckDNS."""
    params = {"domains": domain, "token": token, "ip": ip or "", "verbose": "true"}
    try:
        r = requests.get("https://www.duckdns.org/update", params=params)
        response_text = r.text.strip()
        message.reply(f"Respuesta de DuckDNS: {response_text}")
        return "OK" in response_text
    except Exception as e:
        message.reply(f"Error actualizando DuckDNS: {e}")
        return False
