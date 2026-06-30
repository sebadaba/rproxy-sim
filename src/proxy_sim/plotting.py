"""Funciones de visualización para resultados de simulación.

Cada función toma un `Simulator` ya corrido y grafica con matplotlib.
Devuelven el `plt.Axes` para que el caller pueda personalizar o guardar.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from proxy_sim.simulator import Simulator


def _ensure_ax(ax: plt.Axes | None) -> plt.Axes:
    """Crea un axes nuevo si no se pasó uno."""
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5))
    return ax


def plot_latency_over_time(
    sim: Simulator,
    ax: plt.Axes | None = None,
    show_timeouts: bool = True,
    show_rejections: bool = True,
) -> plt.Axes:
    """Grafica latencia vs tiempo de finalización, marcando timeouts y rechazos.

    Los timeouts se muestran como líneas verticales naranjas; los rechazos como
    líneas verticales rojas. Útil para ver cuándo empieza la saturación.
    """
    ax = _ensure_ax(ax)

    if sim._completion_times:
        ax.scatter(
            sim._completion_times,
            sim._latencies,
            s=2,
            alpha=0.5,
            color="steelblue",
            label="completado",
        )

    if show_timeouts and sim._timeout_times:
        for t in sim._timeout_times:
            ax.axvline(t, color="orange", alpha=0.3, linewidth=0.5)
        ax.scatter([], [], color="orange", alpha=0.6, label="timeout")

    if show_rejections and sim._rejection_times:
        for t in sim._rejection_times:
            ax.axvline(t, color="red", alpha=0.3, linewidth=0.5)
        ax.scatter([], [], color="red", alpha=0.6, label="rechazado")

    ax.set_xlabel("tiempo (s)")
    ax.set_ylabel("latencia (s)")
    ax.set_title("Latencia en el tiempo")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    return ax


def plot_throughput_over_time(
    sim: Simulator,
    ax: plt.Axes | None = None,
    window: float = 100.0,
) -> plt.Axes:
    """Grafica el throughput móvil (rolling average) con ventana configurable.

    Para cada completion, cuenta cuántos completions hubo en los últimos `window`
    segundos y divide por la ventana. Da una vista suavizada de la carga.
    """
    ax = _ensure_ax(ax)

    if not sim._completion_times:
        ax.set_title("Throughput en el tiempo (sin completions)")
        return ax

    times = np.asarray(sim._completion_times)
    n = len(times)
    throughputs = np.empty(n)
    for i, t in enumerate(times):
        idx_start = int(np.searchsorted(times, t - window, side="left"))
        count = i - idx_start + 1
        throughputs[i] = count / window

    ax.plot(times, throughputs, color="steelblue", linewidth=1)
    ax.set_xlabel("tiempo (s)")
    ax.set_ylabel(f"throughput (req/s, ventana={window}s)")
    ax.set_title(f"Throughput en el tiempo (ventana móvil {window}s)")
    ax.grid(True, alpha=0.3)
    return ax


def plot_stage_breakdown_over_time(
    sim: Simulator,
    ax: plt.Axes | None = None,
    window: float = 100.0,
) -> plt.Axes:
    """Grafica el promedio de las 5 etapas de latencia en bins temporales.

    Stacked area: muestra cómo se reparte la latencia media entre las
    5 etapas (espera proxy, CPU request proxy, espera backend, CPU backend,
    CPU response proxy) a lo largo del tiempo.
    """
    ax = _ensure_ax(ax)

    if not sim._completion_times:
        ax.set_title("Desglose de etapas en el tiempo (sin completions)")
        return ax

    times = np.asarray(sim._completion_times)
    t_max = times[-1]
    bins = np.arange(0, t_max + window, window)
    bin_indices = np.digitize(times, bins)

    # (lista_privada, etiqueta_en_leyenda)
    stages = [
        (sim._wait_proxy, "espera proxy"),
        (sim._service_proxy_request, "CPU request proxy"),
        (sim._wait_backend, "espera backend"),
        (sim._service_backend, "CPU backend"),
        (sim._service_proxy_response, "CPU response proxy"),
    ]
    colors = ["#a8e6cf", "#ffd3b6", "#ffaaa5", "#a3c4f3", "#bdb2ff"]

    bin_centers = (bins[:-1] + bins[1:]) / 2
    bottom = np.zeros(len(bin_centers))

    for (values, label), color in zip(stages, colors):
        vals = np.asarray(values)
        means = np.array(
            [
                vals[bin_indices == i].mean() if (bin_indices == i).any() else 0.0
                for i in range(1, len(bins))
            ]
        )
        ax.fill_between(
            bin_centers, bottom, bottom + means, label=label, color=color, alpha=0.7
        )
        bottom += means

    ax.set_xlabel("tiempo (s)")
    ax.set_ylabel(f"latencia media (s, ventana={window}s)")
    ax.set_title(f"Desglose de etapas en el tiempo (bins de {window}s)")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    return ax


def plot_latency_cdf(
    sim: Simulator,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Grafica la CDF de latencias (solo completados, excluye timeouts).

    Marca los percentiles p50, p95 y p99 con líneas verticales y etiquetas.
    """
    ax = _ensure_ax(ax)

    if not sim._latencies:
        ax.set_title("CDF de latencia (sin completions)")
        return ax

    latencies = np.sort(sim._latencies)
    cdf = np.arange(1, len(latencies) + 1) / len(latencies)

    ax.plot(latencies, cdf, color="steelblue", linewidth=1.5)
    for p in [50, 95, 99]:
        v = float(np.percentile(sim._latencies, p))
        ax.axvline(v, color="gray", linestyle="--", alpha=0.5)
        ax.text(v, 0.05, f"p{p}={v * 1000:.1f}ms", rotation=90, fontsize=9, va="bottom")

    ax.set_xlabel("latencia (s)")
    ax.set_ylabel("F(x) = P(T ≤ x)")
    ax.set_title("CDF de latencia (solo completados)")
    ax.grid(True, alpha=0.3)
    return ax