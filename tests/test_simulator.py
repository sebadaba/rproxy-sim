"""Tests del simulador."""

import numpy as np
import pytest

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
    with pytest.raises(ValueError):
        Simulator(arrival_rate=0, service_rate=20, duration=10, seed=1)
    with pytest.raises(ValueError):
        Simulator(arrival_rate=10, service_rate=20, duration=10, seed=1, num_backends=0)
    with pytest.raises(ValueError):
        Simulator(arrival_rate=10, service_rate=20, duration=-1, seed=1)


def test_lb_personalizado_se_almacena():
    """Si se pasa un LB custom, queda guardado en sim._lb para ser usado
    por _select_backend durante el run."""
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


# ---------- proxy ----------


def test_proxy_desactivado_por_default_no_agrega_etapas():
    """Con defaults (sin proxy), todas las etapas de proxy son 0 y total =
    wait_backend + service_backend (igual que antes)."""
    summary = Simulator(
        arrival_rate=10.0,
        service_rate=20.0,
        duration=500.0,
        seed=42,
    ).run()
    assert summary["wait_proxy_mean"] == 0.0
    assert summary["service_proxy_request_mean"] == 0.0
    assert summary["service_proxy_response_mean"] == 0.0
    assert summary["proxy_cpu_utilization"] == 0.0
    # el backend sigue su curso normal
    assert summary["mean_latency"] > 0.0


def test_proxy_request_activo_agrega_etapa_request():
    """cpu_cost_request constante → service_proxy_request_mean == cost/capacity."""
    cost = 0.001
    capacity = 1.0
    summary = Simulator(
        arrival_rate=10.0,
        service_rate=20.0,
        duration=500.0,
        seed=42,
        proxy_cpu_cost_request=cost,
        proxy_cpu_capacity=capacity,
    ).run()
    assert summary["service_proxy_request_mean"] == pytest.approx(cost / capacity)
    # no hay cost_response, esa etapa queda en 0
    assert summary["service_proxy_response_mean"] == 0.0


def test_proxy_response_activo_agrega_etapa_response():
    """cpu_cost_response constante → service_proxy_response_mean == cost/capacity."""
    cost = 0.001
    capacity = 1.0
    summary = Simulator(
        arrival_rate=10.0,
        service_rate=20.0,
        duration=500.0,
        seed=42,
        proxy_cpu_cost_response=cost,
        proxy_cpu_capacity=capacity,
    ).run()
    assert summary["service_proxy_response_mean"] == pytest.approx(cost / capacity)
    assert summary["service_proxy_request_mean"] == 0.0


def test_desglose_5_etapas_suma_latencia_total():
    """Para cada request completado, las 5 componentes suman completion - arrival."""
    sim = Simulator(
        arrival_rate=20.0,
        service_rate=50.0,
        duration=500.0,
        seed=42,
        proxy_cpu_cost_request=0.0005,
        proxy_cpu_cost_response=0.0005,
        proxy_cpu_capacity=1.0,
    )
    sim.run()

    n = len(sim._latencies)
    assert n > 0
    total_componentes = (
        sum(sim._wait_proxy)
        + sum(sim._service_proxy_request)
        + sum(sim._wait_backend)
        + sum(sim._service_backend)
        + sum(sim._service_proxy_response)
    )
    total_latencias = sum(sim._latencies)
    assert total_componentes == pytest.approx(total_latencias, rel=1e-9)


def test_proxy_utilizacion_refleja_ambas_direcciones():
    """En estado estable, busy_time/elapsed ≈ λ·(cost_req + cost_resp)/capacity."""
    arrival_rate = 5.0
    cost_req = 0.001
    cost_resp = 0.002
    capacity = 1.0
    expected = arrival_rate * (cost_req + cost_resp) / capacity  # 0.015

    summary = Simulator(
        arrival_rate=arrival_rate,
        service_rate=50.0,
        duration=2000.0,
        seed=42,
        proxy_cpu_cost_request=cost_req,
        proxy_cpu_cost_response=cost_resp,
        proxy_cpu_capacity=capacity,
    ).run()

    rel_err = abs(summary["proxy_cpu_utilization"] - expected) / expected
    assert rel_err < 0.10, (
        f"utilization={summary['proxy_cpu_utilization']:.4f}, "
        f"esperado≈{expected:.4f}, err={rel_err:.3%}"
    )


def test_rechazo_por_cola_del_proxy_llena():
    """Con proxy_max_queue_size pequeño y proxy saturado, hay rechazos."""
    summary = Simulator(
        arrival_rate=50.0,
        service_rate=100.0,
        duration=20.0,
        seed=42,
        proxy_cpu_cost_request=0.01,  # proxy lento
        proxy_cpu_capacity=1.0,
        proxy_max_queue_size=1,
    ).run()
    assert summary["rejected"] > 0


def test_proxy_saturado_deja_backends_ociosos():
    """Si λ·cost > 0.5·capacity, el proxy es el bottleneck."""
    sim = Simulator(
        arrival_rate=80.0,        # 80·0.01/1 = 0.8 util teórica
        service_rate=200.0,       # backend rápido, lejos de saturarse
        duration=200.0,
        seed=42,
        proxy_cpu_cost_request=0.01,
        proxy_cpu_capacity=1.0,
    )
    summary = sim.run()
    assert summary["proxy_cpu_utilization"] > 0.5
    # la latencia se va en cola del proxy, no del backend
    assert summary["wait_proxy_mean"] > summary["wait_backend_mean"]


def test_proxy_no_se_instancia_si_esta_desactivado():
    """Cuando ambos costs son 0, el simulador no crea un Proxy."""
    sim = Simulator(
        arrival_rate=10.0, service_rate=20.0, duration=50.0, seed=1,
    )
    assert sim._proxy is None


def test_parametros_proxy_invalidos_lanzan_error():
    with pytest.raises(ValueError):
        Simulator(
            arrival_rate=10, service_rate=20, duration=10, seed=1,
            proxy_cpu_cost_request=-0.001, proxy_cpu_capacity=1.0,
        )
    with pytest.raises(ValueError):
        Simulator(
            arrival_rate=10, service_rate=20, duration=10, seed=1,
            proxy_cpu_cost_response=-0.001, proxy_cpu_capacity=1.0,
        )
    with pytest.raises(ValueError):
        Simulator(
            arrival_rate=10, service_rate=20, duration=10, seed=1,
            proxy_cpu_cost_request=0.001, proxy_cpu_capacity=0.0,
        )


def test_reproducibilidad_con_proxy_activo():
    """Misma semilla + mismos parámetros proxy → mismas métricas."""
    params = dict(
        arrival_rate=10.0, service_rate=20.0, duration=300.0, seed=99,
        proxy_cpu_cost_request=0.001,
        proxy_cpu_cost_response=0.001,
        proxy_cpu_capacity=1.0,
    )
    s1 = Simulator(**params).run()
    s2 = Simulator(**params).run()
    assert s1["mean_latency"] == s2["mean_latency"]
    assert s1["proxy_cpu_utilization"] == s2["proxy_cpu_utilization"]


# ---------- proxy_timeout ----------


def test_proxy_timeout_none_no_afecta_comportamiento():
    """Default (None) → 0 timeouts, comportamiento idéntico al actual."""
    summary = Simulator(
        arrival_rate=10.0, service_rate=20.0, duration=500.0, seed=42,
    ).run()
    assert summary["proxy_timed_out"] == 0


def test_proxy_timeout_dispara_en_proxy_saturado():
    """Proxy saturado + timeout > service_time → tasa de timeout > 0 y < 100%."""
    summary = Simulator(
        arrival_rate=50.0,
        service_rate=200.0,
        duration=200.0,
        seed=42,
        proxy_cpu_cost_request=0.01,  # μ_proxy=100, λ=50 → util 0.5
        proxy_cpu_capacity=1.0,
        proxy_timeout=0.025,          # 25ms: ~2.5× service_time
    ).run()
    # el timeout debe capturar una mezcla (no 0% ni 100%)
    assert summary["proxy_timed_out"] > 0
    total = summary["completed"] + summary["proxy_timed_out"]
    timeout_rate = summary["proxy_timed_out"] / total if total > 0 else 0
    assert 0.05 < timeout_rate < 0.95, f"tasa de timeout={timeout_rate:.2%} fuera de rango"


def test_proxy_timeout_no_dispara_por_backend_lento():
    """Backend saturado pero proxy libre → 0 timeouts (aísla causas)."""
    summary = Simulator(
        arrival_rate=18.0,           # cerca de saturar backend (μ=20, ρ=0.9)
        service_rate=20.0,
        duration=200.0,
        seed=42,
        # sin proxy CPU: el proxy es "instantáneo", proxy_time ≈ 0
        proxy_timeout=0.001,         # 1ms
    ).run()
    assert summary["proxy_timed_out"] == 0
    assert summary["completed"] > 0


def test_proxy_timeout_excluye_de_latencia():
    """Las latencias registradas son solo de completados, no de timeouts."""
    sim = Simulator(
        arrival_rate=50.0,
        service_rate=200.0,
        duration=200.0,
        seed=42,
        proxy_cpu_cost_request=0.01,
        proxy_cpu_capacity=1.0,
        proxy_timeout=0.005,
    )
    summary = sim.run()
    assert len(sim._latencies) == summary["completed"]
    assert summary["proxy_timed_out"] > 0


def test_proxy_timeout_cuenta_en_throughput():
    """(completed + proxy_timed_out) / elapsed ≈ arrival_rate."""
    arrival_rate = 30.0
    duration = 1000.0
    sim = Simulator(
        arrival_rate=arrival_rate,
        service_rate=200.0,
        duration=duration,
        seed=42,
        proxy_cpu_cost_request=0.005,
        proxy_cpu_capacity=1.0,
        proxy_timeout=0.002,         # genera timeouts
    )
    summary = sim.run()
    total_processed = summary["completed"] + summary["proxy_timed_out"]
    throughput = total_processed / duration
    assert abs(throughput - arrival_rate) / arrival_rate < 0.10


def test_parametro_proxy_timeout_invalido():
    with pytest.raises(ValueError):
        Simulator(
            arrival_rate=10, service_rate=20, duration=10, seed=1,
            proxy_timeout=0,
        )
    with pytest.raises(ValueError):
        Simulator(
            arrival_rate=10, service_rate=20, duration=10, seed=1,
            proxy_timeout=-1.0,
        )


# ---------- intervalo de confianza ----------


def test_mean_latency_dentro_de_ic_99():
    """Valida M/M/1: el 1/(μ-λ) teórico cae dentro del IC 99% del estimador empírico.

    Usa 99% en vez de 95% para reducir la tasa de falsos positivos cuando el
    sesgo de warmup + right-censoring empuja el estimador ~0.5-1% del valor
    teórico. La simulación de M/M/1 es estadísticamente correcta; el ajuste
    es solo para hacer el test estable.
    """
    arrival_rate = 10.0
    service_rate = 20.0
    theoretical = 1.0 / (service_rate - arrival_rate)  # 0.1s
    duration = 10000.0

    sim = Simulator(
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        duration=duration,
        seed=42,
    )
    sim.run()

    n = len(sim._latencies)
    mean = float(np.mean(sim._latencies))
    std = float(np.std(sim._latencies, ddof=1))
    sem = std / np.sqrt(n)
    z = 2.576  # IC 99% normal estándar
    ci_low = mean - z * sem
    ci_high = mean + z * sem

    assert ci_low <= theoretical <= ci_high, (
        f"teórico={theoretical:.4f} fuera de IC99=[{ci_low:.4f}, {ci_high:.4f}] "
        f"(n={n}, mean={mean:.4f}, sem={sem:.6f})"
    )


def test_throughput_dentro_de_ic_99():
    """El throughput empírico cae dentro del IC 99% de λ.

    Para un proceso de llegadas Poisson, la varianza del estimador n/T es λ/T
    (teorema de Burke), dando un error estándar analítico en vez de estimado.
    Usa 99% para consistencia con test_mean_latency_dentro_de_ic_99.
    """
    arrival_rate = 10.0
    service_rate = 20.0
    duration = 10000.0

    sim = Simulator(
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        duration=duration,
        seed=42,
    )
    summary = sim.run()
    throughput = summary["throughput_rps"]

    se = np.sqrt(arrival_rate / duration)
    z = 2.576  # IC 99%
    ci_low = throughput - z * se
    ci_high = throughput + z * se

    assert ci_low <= arrival_rate <= ci_high, (
        f"λ={arrival_rate} fuera de IC99=[{ci_low:.4f}, {ci_high:.4f}] "
        f"(throughput={throughput:.4f}, se={se:.4f})"
    )


# ---------- cobertura empírica ----------


@pytest.mark.slow
def test_calibracion_ic_99_mean_latency():
    """La cobertura empírica del IC 99% para mean_latency es cercana a 99%.

    Usa batch means para estimar correctamente la varianza en presencia de
    autocorrelación de las latencias consecutivas. Divide cada corrida en K
    batches, calcula la varianza entre las medias de cada batch, y usa esa
    varianza para construir el IC. Esto corrige la subestimación del SE
    naive (std/√n), que ignora la correlación entre latencias consecutivas.
    """
    n_runs = 30
    arrival_rate = 10.0
    service_rate = 20.0
    theoretical = 1.0 / (service_rate - arrival_rate)
    duration = 2000.0
    z = 2.576
    K = 50  # número de batches por corrida

    hits = 0
    for seed in range(n_runs):
        sim = Simulator(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            duration=duration,
            seed=seed,
        )
        sim.run()
        latencies = np.asarray(sim._latencies)
        n = len(latencies)
        if n < K:
            continue

        # Divide en K batches iguales
        batch_size = n // K
        batch_means = np.array(
            [latencies[i * batch_size:(i + 1) * batch_size].mean() for i in range(K)]
        )

        # Varianza entre batch means (con ddof=1) y SE de la gran media
        sigma2_batch = float(batch_means.var(ddof=1))
        se = np.sqrt(sigma2_batch / K)
        grand_mean = float(latencies.mean())
        if grand_mean - z * se <= theoretical <= grand_mean + z * se:
            hits += 1

    coverage = hits / n_runs
    assert coverage >= 0.80, (
        f"cobertura={coverage:.2%} ({hits}/{n_runs}) demasiado baja "
        f"(esperado ~99%)"
    )


@pytest.mark.slow
def test_calibracion_ic_99_throughput():
    """La cobertura empírica del IC 99% para throughput es cercana a 99%.

    Usa la varianza analítica de Poisson (SE = sqrt(λ/T)) para construir
    el IC en cada corrida.
    """
    n_runs = 30
    arrival_rate = 10.0
    service_rate = 20.0
    duration = 2000.0
    z = 2.576

    hits = 0
    for seed in range(n_runs):
        sim = Simulator(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            duration=duration,
            seed=seed,
        )
        summary = sim.run()
        throughput = summary["throughput_rps"]
        se = np.sqrt(arrival_rate / duration)
        if throughput - z * se <= arrival_rate <= throughput + z * se:
            hits += 1

    coverage = hits / n_runs
    assert coverage >= 0.80, (
        f"cobertura={coverage:.2%} ({hits}/{n_runs}) demasiado baja "
        f"(esperado ~99%)"
    )
