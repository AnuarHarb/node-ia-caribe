"""Datos del computador donde corre la prueba, para la nota técnica."""

from __future__ import annotations

import platform
import subprocess


def describir_equipo() -> dict:
    info = {
        "sistema": platform.platform(),
        "python": platform.python_version(),
        "arquitectura": platform.machine(),
        "procesador": "",
        "memoria_gb": None,
    }
    try:
        perfil = subprocess.check_output(
            ["system_profiler", "SPHardwareDataType"],
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return info
    for linea in perfil.splitlines():
        if ":" not in linea:
            continue
        clave, valor = linea.split(":", 1)
        clave = clave.strip()
        valor = valor.strip()
        if clave == "Chip":
            info["procesador"] = valor
        elif clave == "Memory":
            numero = valor.split()[0]
            try:
                info["memoria_gb"] = int(numero)
            except ValueError:
                info["memoria_gb"] = valor
        elif clave == "Model Name" and not info["procesador"]:
            info["procesador"] = valor
    return info


def texto_equipo(info: dict | None = None) -> str:
    info = info or describir_equipo()
    memoria = info.get("memoria_gb")
    memoria_txt = f"{memoria} GB" if memoria else "memoria no leída"
    chip = info.get("procesador") or "procesador no leído"
    return f"{chip}, {memoria_txt}, {info.get('sistema', '')}, Python {info.get('python', '')}"
