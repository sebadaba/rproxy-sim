"""Simulador DES de un reverse proxy con varios backends."""

from proxy_sim.components import Backend, Proxy, Request
from proxy_sim.engine import Event, EventLoop
from proxy_sim.loadbalancers import LoadBalancer, Random, RoundRobin
from proxy_sim.plotting import (
    plot_latency_cdf,
    plot_latency_over_time,
    plot_stage_breakdown_over_time,
    plot_throughput_over_time,
)
from proxy_sim.rng import make_rng
from proxy_sim.simulator import Simulator

__all__ = [
    "Backend",
    "Event",
    "EventLoop",
    "LoadBalancer",
    "Proxy",
    "Random",
    "Request",
    "RoundRobin",
    "Simulator",
    "make_rng",
    "plot_latency_cdf",
    "plot_latency_over_time",
    "plot_stage_breakdown_over_time",
    "plot_throughput_over_time",
]
__version__ = "0.1.0"