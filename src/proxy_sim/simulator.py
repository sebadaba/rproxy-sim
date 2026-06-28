"""Orquestador de la simulación.

Une el EventLoop con los backends, el load balancer y la generación de
llegadas. Por cada REQUEST_ARRIVAL: crea el Request, pide backend al LB y
lo dispatcha (atender o encolar). Por cada SERVICE_COMPLETE: sella la
latencia y promueve el siguiente de la cola.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

import numpy as np

from proxy_sim.components import Backend, Request
from proxy_sim.engine import EventLoop
from proxy_sim.loadbalancers import LoadBalancer, RoundRobin
from proxy_sim.rng import make_rng

if TYPE_CHECKING:
    pass  # placeholder para futuros type hints de Fase 3+


class Simulator:
    """Simulador M/M/k con el LB que se le pase."""

    def __init__(
        self,
        arrival_rate: float,
        service_rate: float,
        duration: float,
        seed: int,
        num_backends: int = 1,
        load_balancer: LoadBalancer | None = None,
        max_queue_size: int | None = None,
    ) -> None:
        if num_backends < 1:
            raise ValueError("num_backends debe ser >= 1")
        if arrival_rate <= 0:
            raise ValueError("arrival_rate debe ser > 0")
        if service_rate <= 0:
            raise ValueError("service_rate debe ser > 0")
        if duration <= 0:
            raise ValueError("duration debe ser > 0")

        self._arrival_rate = arrival_rate
        self._duration = duration
        self._rng = make_rng(seed)
        self._loop = EventLoop(end_time=duration)
        self._backends: list[Backend] = [
            Backend(id=i, mu=service_rate, max_queue_size=max_queue_size)
            for i in range(num_backends)
        ]
        self._lb = load_balancer if load_balancer is not None else RoundRobin()

        self._next_request_id = 0
        self._latencies: list[float] = []
        self._rejected = 0

    def run(self) -> dict:
        """Corre la simulación hasta agotar el tiempo y devuelve el resumen."""
        self._loop.schedule(0.0, self._on_arrival, priority=1)
        self._loop.run()
        return self.summary()

    def summary(self) -> dict:
        """Estadísticas agregadas de la corrida."""
        n = len(self._latencies)
        elapsed = self._loop.now
        if n == 0:
            return {
                "arrival_rate": self._arrival_rate,
                "service_rate": self._backends[0].mu,
                "num_backends": len(self._backends),
                "duration": elapsed,
                "completed": 0,
                "rejected": self._rejected,
                "throughput_rps": 0.0,
                "mean_latency": 0.0,
                "p50_latency": 0.0,
                "p95_latency": 0.0,
                "p99_latency": 0.0,
            }
        arr = np.asarray(self._latencies)
        return {
            "arrival_rate": self._arrival_rate,
            "service_rate": self._backends[0].mu,
            "num_backends": len(self._backends),
            "duration": elapsed,
            "completed": n,
            "rejected": self._rejected,
            "throughput_rps": n / elapsed if elapsed > 0 else 0.0,
            "mean_latency": float(arr.mean()),
            "p50_latency": float(np.percentile(arr, 50)),
            "p95_latency": float(np.percentile(arr, 95)),
            "p99_latency": float(np.percentile(arr, 99)),
        }

    def _on_arrival(self) -> None:
        req = Request(id=self._next_request_id, arrival_time=self._loop.now)
        self._next_request_id += 1

        backend_idx = self._lb.select(self._backends, self._rng)
        backend = self._backends[backend_idx]
        req.backend_id = backend.id

        if not backend.busy():
            self._start_service(backend, req)
        elif backend.is_full():
            req.status = "rejected"
            self._rejected += 1
        else:
            backend.queue.append(req)

        # agenda próximo arrival
        dt = self._rng.exponential(1.0 / self._arrival_rate)
        self._loop.schedule(self._loop.now + dt, self._on_arrival, priority=1)

    def _start_service(self, backend: Backend, req: Request) -> None:
        backend.in_service = req
        req.service_start_time = self._loop.now
        duration = self._rng.exponential(1.0 / backend.mu)
        backend.service_complete_event = self._loop.schedule(
            self._loop.now + duration,
            payload=partial(self._on_service_complete, backend),
            priority=0,
        )

    def _on_service_complete(self, backend: Backend) -> None:
        req = backend.in_service
        assert req is not None, "SERVICE_COMPLETE sin in_service"
        req.completion_time = self._loop.now
        req.status = "completed"
        self._latencies.append(req.completion_time - req.arrival_time)

        backend.in_service = None
        backend.service_complete_event = None

        if backend.queue:
            self._start_service(backend, backend.queue.popleft())