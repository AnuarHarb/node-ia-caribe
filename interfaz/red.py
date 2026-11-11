"""Dirección en la red local para que los teléfonos abran la consulta."""

from __future__ import annotations

import re
import socket

PUERTO_INTERFAZ = 8765
_IPV4 = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")


def ip_en_lan() -> str | None:
    """IPv4 de este equipo en la Wi‑Fi o Ethernet, si se puede detectar."""
    candidatos: list[str] = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sonda:
            sonda.settimeout(0.2)
            sonda.connect(("192.0.2.1", 1))
            candidatos.append(sonda.getsockname()[0])
    except OSError:
        pass
    try:
        nombre = socket.gethostname()
        for familia, _, _, _, direccion in socket.getaddrinfo(nombre, None, socket.AF_INET):
            ip = direccion[0]
            if not ip.startswith("127."):
                candidatos.append(ip)
    except OSError:
        pass
    for ip in candidatos:
        if ip and not ip.startswith("127."):
            return ip
    return candidatos[0] if candidatos else None


def validar_ipv4(texto: str) -> str:
    limpio = (texto or "").strip()
    coincidencia = _IPV4.match(limpio)
    if not coincidencia:
        raise ValueError("IPv4 inválida; usa cuatro números separados por punto, por ejemplo 192.168.1.10")
    octetos = [int(grupo) for grupo in coincidencia.groups()]
    if any(o < 0 or o > 255 for o in octetos):
        raise ValueError("cada grupo de la IP debe estar entre 0 y 255")
    if limpio.startswith("127."):
        raise ValueError("la IP debe ser la de la red local, no 127.0.0.1 (los teléfonos no llegan ahí)")
    return limpio


def enlace_telefono(puerto: int = PUERTO_INTERFAZ, ip_manual: str | None = None) -> dict[str, str]:
    detectada = ip_en_lan() or ""
    origen = "auto"
    ip = detectada
    if ip_manual is not None and str(ip_manual).strip():
        ip = validar_ipv4(str(ip_manual))
        origen = "manual"
    if ip:
        url = f"http://{ip}:{puerto}/voz/telefono"
        texto = url
    else:
        url = f"http://127.0.0.1:{puerto}/voz/telefono"
        texto = f"http://<ip-de-este-equipo>:{puerto}/voz/telefono"
    return {
        "url": url,
        "texto": texto,
        "ip": ip,
        "puerto": str(puerto),
        "origen": origen,
        "ip_detectada": detectada,
    }
