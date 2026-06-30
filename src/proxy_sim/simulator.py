"""Orquestador de la simulación.

Une el EventLoop con los backends, el load balancer, el proxy opcional y la
generación de llegadas. El flujo de un request puede tener hasta 5 etapas:
wait_proxy, service_proxy_request, wait_backend, service_backend,
service_proxy_response. Si el proxy no hace CPU work (costs=0), esas
etapas son 0 y el comportamiento coincide con M/M/k puro.
"""

from __future__ import annotations

from functools import partial

import numpy as np

from proxy_sim.components import Backend, Proxy, Request
from proxy_sim.engine import EventLoop
from proxy_sim.loadbalancers import LoadBalancer, RoundRobin
from proxy_sim.rng import make_rng


class Simulator:
    """Simulador M/M/k con proxy CPU opcional y LB configurable."""

    def __init__(
        self,
        arrival_rate: float,
        service_rate: float,
        duration: float,
        seed: int,
        num_backends: int = 1,
        load_balancer: LoadBalancer | None = None,
        max_queue_size: int | None = None,
        proxy_cpu_cost_request: float = 0.0,
        proxy_cpu_cost_response: float = 0.0,
        proxy_cpu_capacity: float = 1.0,
        proxy_max_queue_size: int | None = None,
    ) -> None:
        if num_backends < 1:
            raise ValueError("num_backends debe ser >= 1")
        if arrival_rate <= 0:
            raise ValueError("arrival_rate debe ser > 0")
        if service_rate <= 0:
            raise ValueError("service_rate debe ser > 0")
        if duration <= 0:
            raise ValueError("duration debe ser > 0")
        if proxy_cpu_cost_request < 0:
            raise ValueError("proxy_cpu_cost_request debe ser >= 0")
        if proxy_cpu_cost_response < 0:
            raise ValueError("proxy_cpu_cost_response debe ser >= 0")
        if proxy_cpu_capacity <= 0:
            raise ValueError("proxy_cpu_capacity debe ser > 0")

        self._arrival_rate = arrival_rate
        self._duration = duration
        self._rng = make_rng(seed)
        self._loop = EventLoop(end_time=duration)
        self._backends: list[Backend] = [
            Backend(id=i, mu=service_rate, max_queue_size=max_queue_size)
            for i in range(num_backends)
        ]
        self._lb = load_balancer if load_balancer is not None else RoundRobin()

        if proxy_cpu_cost_request > 0 or proxy_cpu_cost_response > 0:
            self._proxy: Proxy | None = Proxy(
                cpu_cost_request=proxy_cpu_cost_request,
                cpu_cost_response=proxy_cpu_cost_response,
                cpu_capacity=proxy_cpu_capacity,
                max_queue_size=proxy_max_queue_size,
            )
        else:
            self._proxy = None

        self._next_request_id = 0
        self._latencies: list[float] = []
        self._wait_proxy: list[float] = []
        self._service_proxy_request: list[float] = []
        self._wait_backend: list[float] = []
        self._service_backend: list[float] = []
        self._service_proxy_response: list[float] = []
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
        proxy_util = (
            self._proxy.busy_time / elapsed
            if self._proxy is not None and elapsed > 0
            else 0.0
        )
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
                "wait_proxy_mean": 0.0,
                "service_proxy_request_mean": 0.0,
                "wait_backend_mean": 0.0,
                "service_backend_mean": 0.0,
                "service_proxy_response_mean": 0.0,
                "proxy_cpu_utilization": proxy_util,
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
            "wait_proxy_mean": float(np.mean(self._wait_proxy)),
            "service_proxy_request_mean": float(np.mean(self._service_proxy_request)),
            "wait_backend_mean": float(np.mean(self._wait_backend)),
            "service_backend_mean": float(np.mean(self._service_backend)),
            "service_proxy_response_mean": float(np.mean(self._service_proxy_response)),
            "proxy_cpu_utilization": proxy_util,
        }

    # ---------- helpers ----------

    def _reject(self, req: Request) -> None:
        """Marca el request como rechazado e incrementa el contador global."""
        req.status = "rejected"
        self._rejected += 1

    def _select_backend(self, req: Request) -> Backend:
        """Consulta el LB, marca el backend elegido en el request y lo devuelve."""
        backend_idx = self._lb.select(self._backends, self._rng)
        backend = self._backends[backend_idx]
        req.backend_id = backend.id
        return backend

    # ---------- arrival path ----------

    def _on_arrival(self) -> None:
        req = Request(id=self._next_request_id, arrival_time=self._loop.now)
        self._next_request_id += 1

        if self._proxy is not None and self._proxy.cpu_cost_request > 0:
            self._enqueue_request_at_proxy(req)
        else:
            # sin proxy o sin costo de request: dispatch directo al backend
            req.proxy_start_time = req.arrival_time
            req.dispatch_time = req.arrival_time
            self._dispatch_request_to_backend(req)

        dt = self._rng.exponential(1.0 / self._arrival_rate)
        self._loop.schedule(self._loop.now + dt, self._on_arrival, priority=1)

    def _enqueue_request_at_proxy(self, req: Request) -> None:
        """Admite el request en el proxy.

        Si el proxy está libre, inicia el CPU del request de inmediato.
        Si está ocupado pero la cola tiene espacio, encola el request.
        Si la cola está llena, lo rechaza.
        """
        if not self._proxy.busy():
            self._start_proxy_cpu_service(req)
            return
        if not self._proxy.is_full():
            self._proxy.queue.append(req)
            return
        self._reject(req)

    def _start_proxy_cpu_service(self, req: Request) -> None:
        """Inicia el CPU del proxy sobre el request.

        Si el request aún no hizo CPU request (proxy_start_time es None),
        inicia la fase request. Si ya hizo request CPU, inicia la fase response.
        El phase se deduce del estado del request para mantener una única
        convención en todo el simulador.
        """
        assert self._proxy is not None
        self._proxy.in_service = req

        if req.proxy_start_time is None:
            req.proxy_start_time = self._loop.now
            duration = self._proxy.request_service_time()
            phase = "request"
        else:
            req.response_start_time = self._loop.now
            duration = self._proxy.response_service_time()
            phase = "response"

        self._proxy.service_complete_event = self._loop.schedule(
            self._loop.now + duration,
            payload=partial(self._on_proxy_work_complete, self._proxy, phase),
            priority=0,
        )

    def _on_proxy_work_complete(self, proxy: Proxy, phase: str) -> None:
        req = proxy.in_service
        assert req is not None, "proxy work complete sin in_service"

        if phase == "request":
            proxy.busy_time += self._loop.now - req.proxy_start_time
            req.dispatch_time = self._loop.now
        else:  # response
            proxy.busy_time += self._loop.now - req.response_start_time

        proxy.in_service = None
        proxy.service_complete_event = None

        if phase == "request":
            self._dispatch_request_to_backend(req)
        else:
            self._finalize_request(req)

        # promueve siguiente de la cola mixta del proxy
        if proxy.queue:
            self._start_proxy_cpu_service(proxy.queue.popleft())

    # ---------- backend path ----------

    def _dispatch_request_to_backend(self, req: Request) -> None:
        """Envía el request al backend elegido por el LB.

        Si el backend está libre, inicia el servicio de inmediato.
        Si está ocupado pero la cola tiene espacio, encola.
        Si la cola está llena, rechaza.
        """
        backend = self._select_backend(req)
        if not backend.busy():
            self._start_service(backend, req)
            return
        if not backend.is_full():
            backend.queue.append(req)
            return
        self._reject(req)

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

        req.backend_done_time = self._loop.now

        backend.in_service = None
        backend.service_complete_event = None

        if backend.queue:
            self._start_service(backend, backend.queue.popleft())

        # ¿Falta CPU de response en el proxy?
        if self._proxy is not None and self._proxy.cpu_cost_response > 0:
            self._start_proxy_response_after_backend(req)
        else:
            self._finalize_request(req)

    def _start_proxy_response_after_backend(self, req: Request) -> None:
        """Manda el request al proxy para hacer el CPU del response.

        Si el proxy está libre, inicia el response-CPU de inmediato.
        Si está ocupado pero la cola tiene espacio, encola.
        Si la cola está llena, rechaza.
        """
        if not self._proxy.busy():
            self._start_proxy_cpu_service(req)
            return
        if not self._proxy.is_full():
            self._proxy.queue.append(req)
            return
        self._reject(req)

    # ---------- response path ----------

    def _finalize_request(self, req: Request) -> None:
        req.completion_time = self._loop.now
        req.status = "completed"

        arrival = req.arrival_time
        completion = req.completion_time
        proxy_start = req.proxy_start_time if req.proxy_start_time is not None else arrival
        dispatch = req.dispatch_time if req.dispatch_time is not None else proxy_start
        backend_start = req.service_start_time if req.service_start_time is not None else dispatch
        backend_done = req.backend_done_time if req.backend_done_time is not None else completion
        response_start = req.response_start_time if req.response_start_time is not None else completion

        # wait_proxy acumula espera tanto del lado request como del lado response
        wait_proxy_req = max(0.0, proxy_start - arrival)
        wait_proxy_resp = max(0.0, response_start - backend_done)
        self._wait_proxy.append(wait_proxy_req + wait_proxy_resp)

        self._service_proxy_request.append(max(0.0, dispatch - proxy_start))
        self._wait_backend.append(max(0.0, backend_start - dispatch))
        self._service_backend.append(max(0.0, backend_done - backend_start))
        self._service_proxy_response.append(max(0.0, completion - response_start))
        self._latencies.append(completion - arrival)