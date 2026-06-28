"""Load balancers: eligen backend para cada request entrante."""

from __future__ import annotations

from typing import Protocol

import numpy as np

from proxy_sim.components import Backend


class LoadBalancer(Protocol):
    """Interfaz común: dado el pool y un RNG, devuelve el índice del backend."""

    def select(self, backends: list[Backend], rng: np.random.Generator) -> int:
        ...


class RoundRobin:
    """Round-robin: rota secuencialmente sobre los backends."""

    def __init__(self) -> None:
        self._counter = 0

    def select(self, backends: list[Backend], rng: np.random.Generator) -> int:
        idx = self._counter
        self._counter = (self._counter + 1) % len(backends)
        return idx

    def __repr__(self) -> str:
        return f"RoundRobin(counter={self._counter})"


class Random:
    """Random uniforme: elige backend al azar."""

    def select(self, backends: list[Backend], rng: np.random.Generator) -> int:
        return int(rng.integers(0, len(backends)))

    def __repr__(self) -> str:
        return "Random()"