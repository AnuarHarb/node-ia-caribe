"""Colas de eventos para el avance en vivo (SSE)."""

from __future__ import annotations

import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EstadoCorrida:
    demo_id: int
    corriendo: bool = False
    historial: deque = field(default_factory=lambda: deque(maxlen=500))
    suscriptores: list = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def emitir(self, tipo: str, mensaje: str, datos: dict | None = None) -> None:
        evento = {
            "t": time.time(),
            "tipo": tipo,
            "mensaje": mensaje,
            "datos": datos or {},
        }
        with self._lock:
            self.historial.append(evento)
            copia = list(self.suscriptores)
        linea = f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"
        for cola in copia:
            try:
                cola.put(linea)
            except Exception:
                pass

    def suscribir(self) -> "queue.Queue[str]":
        import queue

        cola: queue.Queue[str] = queue.Queue()
        with self._lock:
            for previo in self.historial:
                cola.put(f"data: {json.dumps(previo, ensure_ascii=False)}\n\n")
            self.suscriptores.append(cola)
        return cola

    def desuscribir(self, cola: Any) -> None:
        with self._lock:
            if cola in self.suscriptores:
                self.suscriptores.remove(cola)


class Bus:
    def __init__(self) -> None:
        self._estados: dict[int, EstadoCorrida] = {}
        self._lock = threading.Lock()

    def de(self, demo_id: int) -> EstadoCorrida:
        with self._lock:
            if demo_id not in self._estados:
                self._estados[demo_id] = EstadoCorrida(demo_id=demo_id)
            return self._estados[demo_id]


BUS = Bus()
