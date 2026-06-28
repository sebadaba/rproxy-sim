"""Tests del simulador."""

from proxy_sim.loadbalancers import RoundRobin
from proxy_sim.simulator import Simulator


def test_smoke_el_simulador_corre_y_devuelve_resumen():
    sim = Simulator(
        arrival_rate=10.0,
        service_rate=20.0,
        duration=100.0,
        seed=42,
    )
    summary = sim.run()
    assert summary["completed"] > 0
    assert summary["duration"] <= 100.0
    assert summary["rejected"] == 0  # sin tope de cola, no hay rechazos


def test_mean_latency_coincide_con_mm1():
    """Validación empírica: E[latency] ≈ 1/(μ − λ) para M/M/1 con k=1."""
    arrival_rate = 10.0
    service_rate = 20.0
    duration = 10000.0
    expected = 1.0 / (service_rate - arrival_rate)  # 0.1s

    summary = Simulator(
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        duration=duration,
        seed=42,
    ).run()
    mean = summary["mean_latency"]

    # 5% tolerancia relativa; con n≈100k el error estadístico es ~0.3%
    rel_err = abs(mean - expected) / expected
    assert rel_err < 0.05, f"mean={mean:.4f}, esperado≈{expected:.4f}, err={rel_err:.3%}"


def test_reproducibilidad_con_mismo_seed():
    params = dict(
        arrival_rate=10.0,
        service_rate=20.0,
        duration=500.0,
        seed=123,
    )
    s1 = Simulator(**params).run()
    s2 = Simulator(**params).run()
    assert s1["mean_latency"] == s2["mean_latency"]
    assert s1["completed"] == s2["completed"]


def test_semillas_distintas_dan_latencias_distintas():
    base = dict(arrival_rate=10.0, service_rate=20.0, duration=500.0)
    s1 = Simulator(seed=1, **base).run()
    s2 = Simulator(seed=999, **base).run()
    assert s1["mean_latency"] != s2["mean_latency"]


def test_rechazo_cuando_cola_se_llena():
    """Con max_queue_size pequeño y λ alto, hay rechazos."""
    summary = Simulator(
        arrival_rate=30.0,
        service_rate=20.0,
        duration=50.0,
        seed=42,
        max_queue_size=1,
    ).run()
    assert summary["rejected"] > 0
    assert summary["completed"] > 0


def test_parametros_invalidos_lanzan_error():
    import pytest

    with pytest.raises(ValueError):
        Simulator(arrival_rate=0, service_rate=20, duration=10, seed=1)
    with pytest.raises(ValueError):
        Simulator(arrival_rate=10, service_rate=20, duration=10, seed=1, num_backends=0)
    with pytest.raises(ValueError):
        Simulator(arrival_rate=10, service_rate=20, duration=-1, seed=1)


def test_lb_personalizado_se_usa():
    """Si se pasa un LB custom, es el que recibe las selecciones."""
    rr = RoundRobin()
    sim = Simulator(
        arrival_rate=50.0,
        service_rate=20.0,
        duration=10.0,
        seed=1,
        load_balancer=rr,
    )
    assert sim._lb is rr


def test_throughput_aproxima_arrival_rate_en_estado_estable():
    """Con λ=10 estable, throughput de completados ≈ 10 req/s."""
    summary = Simulator(
        arrival_rate=10.0,
        service_rate=20.0,
        duration=5000.0,
        seed=7,
    ).run()
    assert abs(summary["throughput_rps"] - 10.0) / 10.0 < 0.05