"""Tests smoke de las funciones de plotting.

Solo verifican que las funciones no crashean con datos válidos. No validan
el rendering gráfico (los pixeles no se prueban en CI).
"""

import matplotlib

matplotlib.use("Agg")  # backend sin display, para CI

import matplotlib.pyplot as plt
import pytest

from proxy_sim import (
    Simulator,
    plot_latency_cdf,
    plot_latency_over_time,
    plot_stage_breakdown_over_time,
    plot_throughput_over_time,
)


def _sim_basico() -> Simulator:
    return Simulator(
        arrival_rate=10.0, service_rate=20.0, duration=100.0, seed=42,
    ).run() is None or Simulator(
        arrival_rate=10.0, service_rate=20.0, duration=100.0, seed=42,
    )


def _sim_con_proxy_y_timeout() -> Simulator:
    sim = Simulator(
        arrival_rate=50.0,
        service_rate=200.0,
        duration=200.0,
        seed=42,
        proxy_cpu_cost_request=0.01,
        proxy_cpu_capacity=1.0,
        proxy_timeout=0.025,
    )
    sim.run()
    return sim


def _sim_con_rechazos() -> Simulator:
    sim = Simulator(
        arrival_rate=30.0,
        service_rate=20.0,
        duration=50.0,
        seed=42,
        max_queue_size=1,
    )
    sim.run()
    return sim


def test_plot_latency_over_time_no_crashea():
    sim = _sim_basico()
    _, ax = plt.subplots()
    result = plot_latency_over_time(sim, ax=ax)
    assert result is ax
    plt.close("all")


def test_plot_latency_over_time_con_timeouts_y_rechazos():
    sim = _sim_con_proxy_y_timeout()
    fig, ax = plt.subplots()
    plot_latency_over_time(sim, ax=ax, show_timeouts=True, show_rejections=True)
    plt.close("all")


def test_plot_throughput_over_time_no_crashea():
    sim = _sim_basico()
    _, ax = plt.subplots()
    result = plot_throughput_over_time(sim, ax=ax, window=20.0)
    assert result is ax
    plt.close("all")


def test_plot_stage_breakdown_over_time_no_crashea():
    sim = _sim_basico()
    _, ax = plt.subplots()
    result = plot_stage_breakdown_over_time(sim, ax=ax, window=20.0)
    assert result is ax
    plt.close("all")


def test_plot_latency_cdf_no_crashea():
    sim = _sim_basico()
    _, ax = plt.subplots()
    result = plot_latency_cdf(sim, ax=ax)
    assert result is ax
    plt.close("all")


def test_plot_funciones_aceptan_ax_existente_y_devuelven_el_mismo():
    """Cada función devuelve el mismo ax que recibió, o uno nuevo si no se pasó."""
    sim = _sim_basico()
    fig, ax = plt.subplots()
    assert plot_latency_over_time(sim, ax=ax) is ax
    assert plot_throughput_over_time(sim, ax=ax) is ax
    assert plot_stage_breakdown_over_time(sim, ax=ax) is ax
    assert plot_latency_cdf(sim, ax=ax) is ax
    plt.close("all")


def test_plot_funciones_crean_figura_si_no_hay_ax():
    """Si ax=None, crean una figura nueva y devuelven el ax de esa figura."""
    sim = _sim_basico()
    for fn in (plot_latency_over_time, plot_throughput_over_time,
               plot_stage_breakdown_over_time, plot_latency_cdf):
        result = fn(sim)
        assert isinstance(result, plt.Axes)
        plt.close("all")