import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Permite importar desde src/
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from rproxy_sim.des_loss import run_replicas, erlang_b


def main():
    arrival_rate = 8.0
    service_rate = 1.0
    capacity = 10
    simulation_time = 1000
    replicas = 30
    seed = 1234

    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    results = run_replicas(
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        capacity=capacity,
        simulation_time=simulation_time,
        replicas=replicas,
        seed=seed,
    )

    df = pd.DataFrame(results)

    simulated_mean = df["blocking_probability"].mean()
    simulated_std = df["blocking_probability"].std(ddof=1)
    ci95 = 1.96 * simulated_std / (replicas ** 0.5)

    theoretical = erlang_b(
        offered_load=arrival_rate / service_rate,
        capacity=capacity,
    )

    relative_error = abs(simulated_mean - theoretical) / theoretical

    csv_path = results_dir / "validation_erlang_b_replicas.csv"
    txt_path = results_dir / "validation_erlang_b_summary.txt"
    png_path = results_dir / "validation_erlang_b_plot.png"

    df.to_csv(csv_path, index=False)

    summary = f"""
Validacion Erlang B - Simulador DES minimo
==========================================

Parametros:
arrival_rate = {arrival_rate}
service_rate = {service_rate}
capacity = {capacity}
simulation_time = {simulation_time}
replicas = {replicas}

Resultados:
bloqueo_promedio_simulado = {simulated_mean}
desviacion_estandar = {simulated_std}
intervalo_confianza_95 = [{simulated_mean - ci95}, {simulated_mean + ci95}]
erlang_b_teorico = {theoretical}
error_relativo = {relative_error}

Archivos generados:
{csv_path}
{png_path}
"""

    txt_path.write_text(summary, encoding="utf-8")

    print(summary)

    plt.figure()
    plt.plot(df["replica"], df["blocking_probability"], marker="o", label="Replica")
    plt.axhline(simulated_mean, linestyle="--", label="Promedio simulado")
    plt.axhline(theoretical, linestyle=":", label="Erlang B teorico")
    plt.xlabel("Replica")
    plt.ylabel("Probabilidad de bloqueo")
    plt.title("Validacion del simulador DES minimo contra Erlang B")
    plt.legend()
    plt.grid(True)
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    main()