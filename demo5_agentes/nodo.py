"""Aislamiento de archivos entre agentes de distintas entidades.

Cada agente solo puede leer y escribir dentro de su caja. El intento de salir
queda en un registro de auditoría con cadena de hashes. Es un prototipo de
laboratorio: la mediación ocurre en las herramientas del agente, no en cuentas
separadas del sistema operativo.
"""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path


class AccesoDenegado(PermissionError):
    def __init__(self, motivo: str, ruta: str):
        self.motivo = motivo
        self.ruta = ruta
        super().__init__(motivo)


def _canon(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class RegistroAuditoria:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def eventos(self) -> list[dict]:
        texto = self.path.read_text(encoding="utf-8")
        return [json.loads(linea) for linea in texto.splitlines() if linea.strip()]

    def registrar(
        self,
        entidad: str,
        accion: str,
        ruta: str,
        resultado: str,
        motivo: str,
    ) -> dict:
        with self._lock:
            previos = self.eventos()
            prev = previos[-1]["hash"] if previos else "0" * 64
            cuerpo = {
                "n": len(previos) + 1,
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "entidad": entidad,
                "accion": accion,
                "ruta": ruta,
                "resultado": resultado,
                "motivo": motivo,
                "prev": prev,
            }
            cuerpo["hash"] = hashlib.sha256(_canon(cuerpo).encode("utf-8")).hexdigest()
            with self.path.open("a", encoding="utf-8") as archivo:
                archivo.write(_canon(cuerpo) + "\n")
            return cuerpo

    def integra(self) -> bool:
        prev = "0" * 64
        try:
            eventos = self.eventos()
        except json.JSONDecodeError:
            return False
        for evento in eventos:
            declarado = evento.get("hash")
            cuerpo = {clave: valor for clave, valor in evento.items() if clave != "hash"}
            if cuerpo.get("prev") != prev:
                return False
            if hashlib.sha256(_canon(cuerpo).encode("utf-8")).hexdigest() != declarado:
                return False
            prev = declarado
        return True


class Nodo:
    def __init__(self, raiz: Path | str):
        self.raiz = Path(raiz)
        self.raiz.mkdir(parents=True, exist_ok=True)
        (self.raiz / "entidades").mkdir(exist_ok=True)
        self.auditoria = RegistroAuditoria(self.raiz / "auditoria.jsonl")

    def abrir(self, entidad: str) -> Agente:
        if not _id_entidad_valido(entidad):
            raise ValueError("identificador de entidad inválido")
        caja = self.raiz / "entidades" / entidad
        caja.mkdir(exist_ok=True)
        return Agente(entidad, caja, self)


def _id_entidad_valido(entidad: str) -> bool:
    if not entidad or entidad in {".", ".."}:
        return False
    prohibido = set("/\\\x00")
    return not any(caracter in prohibido for caracter in entidad)


class Agente:
    def __init__(self, entidad: str, caja: Path, nodo: Nodo):
        self.entidad = entidad
        self.caja = caja
        self._nodo = nodo

    def escribir(self, ruta: str, contenido: str) -> None:
        try:
            destino = self._dentro(ruta)
            if destino.is_symlink():
                raise AccesoDenegado("enlace_simbolico", ruta)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(contenido, encoding="utf-8")
        except AccesoDenegado as exc:
            self._auditar("escribir", ruta, "denegado", exc.motivo)
            raise
        self._auditar("escribir", ruta, "permitido", "dentro_de_la_entidad")

    def leer(self, ruta: str) -> str:
        try:
            destino = self._dentro(ruta)
            if _es_enlace(self.caja, ruta) or not destino.is_file():
                motivo = "enlace_simbolico" if _es_enlace(self.caja, ruta) else "no_existe"
                if not destino.is_relative_to(self.caja.resolve()):
                    motivo = "fuera_del_aislamiento"
                raise AccesoDenegado(motivo, ruta)
            texto = destino.read_text(encoding="utf-8")
        except AccesoDenegado as exc:
            self._auditar("leer", ruta, "denegado", exc.motivo)
            raise
        self._auditar("leer", ruta, "permitido", "dentro_de_la_entidad")
        return texto

    def listar(self) -> list[str]:
        base = self.caja.resolve()
        nombres: list[str] = []
        for path in sorted(self.caja.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue
            if path.resolve().is_relative_to(base):
                nombres.append(path.relative_to(self.caja).as_posix())
        self._auditar("listar", ".", "permitido", "dentro_de_la_entidad")
        return nombres

    def _dentro(self, ruta: str) -> Path:
        if not isinstance(ruta, str) or ruta.strip() == "" or "\x00" in ruta:
            raise AccesoDenegado("ruta_invalida", str(ruta))
        if Path(ruta).is_absolute():
            raise AccesoDenegado("fuera_del_aislamiento", ruta)
        base = self.caja.resolve()
        try:
            destino = (base / ruta).resolve()
        except OSError as exc:
            raise AccesoDenegado("ruta_invalida", ruta) from exc
        if not destino.is_relative_to(base):
            raise AccesoDenegado("fuera_del_aislamiento", ruta)
        return destino

    def _auditar(self, accion: str, ruta: str, resultado: str, motivo: str) -> None:
        self._nodo.auditoria.registrar(self.entidad, accion, ruta, resultado, motivo)


def _es_enlace(caja: Path, ruta: str) -> bool:
    actual = caja
    for parte in Path(ruta).parts:
        if parte in {"", "."}:
            continue
        if parte == "..":
            return False
        actual = actual / parte
        if actual.is_symlink():
            return True
        if not actual.exists():
            return False
    return False
