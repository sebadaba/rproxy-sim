"""Entidades del dominio: Request y Backend."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from proxy_sim.engine import Event


@dataclass
class Request:
    """Un request que viaja por el sistema.

    Se crea al llegar al proxy con solo id y arrival_time; el resto se va
    llenando conforme avanza (despacho, inicio de servicio, fin).
    """

    id: int
    arrival_time: float
    backend_id: int | None = None
    service_start_time: float | None = None
    completion_time: float | None = None
    status: Literal["pending", "completed", "rejected", "timeout"] = "pending"


class Backend:
    """Un servidor con su cola FIFO.

    Estado pasivo: la lógica de despachar/atender vive en simulator.py.
    El campo `service_complete_event` guarda la referencia al evento
    agendado de fin de servicio, para cancelación lógica si la cola cambia.
    """

    def __init__(
        self,
        id: int,
        mu: float,
        max_queue_size: int | None = None,
    ) -> None:
        self.id = id
        self.mu = mu  # tasa de servicio (req/s). E[service_time] = 1/mu.
        self.max_queue_size = max_queue_size  # None = cola infinita
        self.queue: deque[Request] = deque()
        self.in_service: Request | None = None
        self.service_complete_event: Event | None = None

    def busy(self) -> bool:
        """True si está atendiendo un request ahora."""
        return self.in_service is not None

    def qlen(self) -> int:
        """Largo actual de la cola de espera."""
        return len(self.queue)

    def load(self) -> int:
        """Carga lógica: 1 si está ocupado + largo de cola.

        Útil para LeastConnections y Power-of-Two-Choices.
        """
        return (1 if self.in_service else 0) + len(self.queue)

    def is_full(self) -> bool:
        """True si la cola alcanzó el tope configurado (si hay tope)."""
        return self.max_queue_size is not None and len(self.queue) >= self.max_queue_size