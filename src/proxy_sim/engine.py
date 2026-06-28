"""Motor de simulación de eventos discretos (DES)."""

from __future__ import annotations

import heapq
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class Event:
    """Un evento agendado en la simulación.

    Orden en el heap: (time, priority, seq).
    - time: hora absoluta de ejecución.
    - priority: desempate en igual timestamp; menor valor primero (0 = SERVICE_COMPLETE).
    - seq: orden de inserción, garantiza FIFO si time y priority coinciden.
    - payload: función sin argumentos que se ejecuta al disparar el evento.
    """

    time: float = field(compare=True)
    priority: int = field(compare=True)
    seq: int = field(compare=True)
    payload: Callable[[], Any] = field(compare=False, repr=False)


class EventLoop:
    """Loop cronológico de eventos sobre un heap binario."""

    def __init__(self, end_time: float, start_time: float = 0.0) -> None:
        if end_time < start_time:
            raise ValueError(
                f"end_time ({end_time}) debe ser >= start_time ({start_time})"
            )
        self.now: float = start_time
        self.end_time: float = end_time
        self._pq: list[Event] = []
        self._seq: int = 0

    def schedule(
        self,
        time: float,
        payload: Callable[[], Any],
        priority: int = 0,
    ) -> Event:
        """Agenda payload() para correr en time (absoluto).

        Devuelve el Event, útil para cancelación lógica posterior.
        """
        if time < self.now:
            raise ValueError(
                f"no se puede agendar en el pasado: t={time} < now={self.now}"
            )
        ev = Event(time=time, priority=priority, seq=self._seq, payload=payload)
        self._seq += 1
        heapq.heappush(self._pq, ev)
        return ev

    def peek_next_time(self) -> float | None:
        """Hora del próximo evento, o None si el heap está vacío."""
        return self._pq[0].time if self._pq else None

    def is_empty(self) -> bool:
        return not self._pq

    def run(self) -> None:
        """Procesa eventos hasta vaciar o pasar end_time."""
        while self._pq and self._pq[0].time <= self.end_time:
            ev = heapq.heappop(self._pq)
            self.now = ev.time
            ev.payload()

    def __len__(self) -> int:
        return len(self._pq)

    def __repr__(self) -> str:
        return (
            f"EventLoop(now={self.now}, end_time={self.end_time}, "
            f"pending={len(self._pq)})"
        )