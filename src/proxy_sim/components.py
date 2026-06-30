"""Entidades del dominio: Request, Backend y Proxy."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass
class Request:
    """Un request que viaja por el sistema.

    Se crea al llegar al proxy con arrival_time. El resto se va llenando
    conforme avanza: proxy CPU (request), dispatch al backend, servicio en
    backend, y proxy CPU (response) si está configurado.
    """

    id: int
    arrival_time: float
    backend_id: int | None = None
    service_start_time: float | None = None
    backend_done_time: float | None = None  # fin del backend (antes de response CPU)
    completion_time: float | None = None
    status: Literal["pending", "completed", "rejected", "timeout"] = "pending"
    proxy_start_time: float | None = None  # inicio de CPU request en proxy
    dispatch_time: float | None = None    # fin de CPU request (= listo para backend)
    response_start_time: float | None = None  # inicio de CPU response en proxy


class Backend:
    """Un servidor con su cola FIFO."""

    def __init__(
        self,
        id: int,
        mu: float,
        max_queue_size: int | None = None,
    ) -> None:
        self.id = id
        self.mu = mu
        self.max_queue_size = max_queue_size
        self.queue: deque[Request] = deque()
        self.in_service: Request | None = None

    def busy(self) -> bool:
        """True si está atendiendo un request ahora."""
        return self.in_service is not None

    def qlen(self) -> int:
        """Largo actual de la cola de espera."""
        return len(self.queue)

    def load(self) -> int:
        """1 si está ocupado + largo de cola. Útil para LeastConnections."""
        return (1 if self.in_service else 0) + len(self.queue)

    def is_full(self) -> bool:
        """True si la cola alcanzó el tope configurado (si hay tope)."""
        return self.max_queue_size is not None and len(self.queue) >= self.max_queue_size

    def sample_service_time(self, rng: np.random.Generator) -> float:
        """Devuelve una muestra de tiempo de servicio ~ Exp(1/μ)."""
        return rng.exponential(1.0 / self.mu)


class Proxy:
    """Nodo M/M/1 que modela el trabajo CPU del proxy.

    Hace CPU work en dos momentos por request:
    1. Request: parsear, validar, dispatchar (costo cpu_cost_request).
    2. Response: parsear respuesta, escribir al cliente (costo cpu_cost_response).

    Ambos comparten la misma cola y CPU. Si uno de los dos costos es 0,
    esa etapa es instantánea.
    """

    def __init__(
        self,
        cpu_cost_request: float,
        cpu_cost_response: float,
        cpu_capacity: float,
        max_queue_size: int | None = None,
    ) -> None:
        if cpu_cost_request < 0:
            raise ValueError("cpu_cost_request debe ser >= 0")
        if cpu_cost_response < 0:
            raise ValueError("cpu_cost_response debe ser >= 0")
        if cpu_cost_request == 0 and cpu_cost_response == 0:
            raise ValueError("Proxy requiere al menos uno de cost_request/cost_response > 0")
        if cpu_capacity <= 0:
            raise ValueError("cpu_capacity debe ser > 0")

        self.cpu_cost_request = cpu_cost_request
        self.cpu_cost_response = cpu_cost_response
        self.cpu_capacity = cpu_capacity
        self.max_queue_size = max_queue_size
        self.queue: deque[Request] = deque()
        self.in_service: Request | None = None
        self.busy_time: float = 0.0  # acumulado de tiempo con CPU ocupada

    def busy(self) -> bool:
        return self.in_service is not None

    def qlen(self) -> int:
        return len(self.queue)

    def load(self) -> int:
        return (1 if self.in_service else 0) + len(self.queue)

    def is_full(self) -> bool:
        return self.max_queue_size is not None and len(self.queue) >= self.max_queue_size

    def request_service_time(self) -> float:
        """Tiempo de CPU por request del lado del request."""
        return self.cpu_cost_request / self.cpu_capacity

    def response_service_time(self) -> float:
        """Tiempo de CPU por request del lado del response."""
        return self.cpu_cost_response / self.cpu_capacity