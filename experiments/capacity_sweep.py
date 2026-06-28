import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from rproxy_sim.des_loss import run_replicas


def confidence_interval_95(series):
    n = len(series)
    mean = series.mean()
    std = series.std(ddof=1)
    half_width = 1.96 * std / (n ** 0.5)
    return mean, mean - half_width, mean + half_width


def main():
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    simulation_time = 1000
    replicas = 30
    seed = 341

    # Carga exigente similar al escenario corredor_metro_comercial
    arrival_rate = 11.25
    service_rate = 1.0

    capacities = [6, 8, 10, 12, 14, 16, 20, 24, 30]

    all_rows = []

    for capacity in capacities:
        replica_results = run_replicas(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            capacity=capacity,
            simulation_time=simulation_time,
            replicas=replicas,
            seed=seed + capacity,
        )

        for row in replica_results:
            row["capacity"] = capacity
            row["arrival_rate"] = arrival_rate
            row["service_rate"] = service_rate
            all_rows.append(row)

    df = pd.DataFrame(all_rows)

    summary_rows = []

    for capacity, group in df.groupby("capacity"):
        bp_mean, bp_low, bp_high = confidence_interval_95(group["blocking_probability"])
        util_mean, util_low, util_high = confidence_interval_95(group["utilization"])

        summary_rows.append(
            {
                "capacity": capacity,
                "arrival_rate": arrival_rate,
                "service_rate": service_rate,
                "blocking_probability_mean": bp_mean,
                "blocking_probability_ci95_low": bp_low,
                "blocking_probability_ci95_high": bp_high,
                "utilization_mean": util_mean,
                "utilization_ci95_low": util_low,
                "utilization_ci95_high": util_high,
                "mean_rejected": group["rejected"].mean(),
                "mean_accepted": group["accepted"].mean(),
                "mean_arrivals": group["arrivals"].mean(),
            }
        )

    summary_df = pd.DataFrame(summary_rows).sort_values("capacity")

    csv_path = results_dir / "capacity_sweep_replicas.csv"
    summary_csv_path = results_dir / "capacity_sweep_summary.csv"
    txt_path = results_dir / "capacity_sweep_summary.txt"

    df.to_csv(csv_path, index=False)
    summary_df.to_csv(summary_csv_path, index=False)

    target = 0.05
    feasible = summary_df[summary_df["blocking_probability_mean"] <= target]

    if len(feasible) > 0:
        min_capacity = int(feasible.iloc[0]["capacity"])
        recommendation = (
            f"La menor capacidad evaluada que deja el bloqueo promedio bajo {target:.0%} "
            f"es c = {min_capacity}."
        )
    else:
        recommendation = (
            f"Ninguna capacidad evaluada logro dejar el bloqueo promedio bajo {target:.0%}."
        )

    txt = "Barrido de capacidad - Reverse Proxy DES\n"
    txt += "=======================================\n\n"
    txt += f"simulation_time = {simulation_time}\n"
    txt += f"replicas = {replicas}\n"
    txt += f"arrival_rate = {arrival_rate}\n"
    txt += f"service_rate = {service_rate}\n"
    txt += f"capacities = {capacities}\n\n"
    txt += summary_df.to_string(index=False)
    txt += "\n\n"
    txt += recommendation
    txt += "\n"

    txt_path.write_text(txt, encoding="utf-8")

    print(txt)

    plt.figure()
    plt.errorbar(
        summary_df["capacity"],
        summary_df["blocking_probability_mean"],
        yerr=[
            summary_df["blocking_probability_mean"] - summary_df["blocking_probability_ci95_low"],
            summary_df["blocking_probability_ci95_high"] - summary_df["blocking_probability_mean"],
        ],
        marker="o",
        capsize=5,
    )
    plt.axhline(target, linestyle="--", label="Umbral 5%")
    plt.xlabel("Capacidad del reverse proxy")
    plt.ylabel("Probabilidad de bloqueo")
    plt.title("Efecto de la capacidad sobre la probabilidad de bloqueo")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "capacity_sweep_blocking_probability.png", dpi=300)
    plt.close()

    plt.figure()
    plt.errorbar(
        summary_df["capacity"],
        summary_df["utilization_mean"],
        yerr=[
            summary_df["utilization_mean"] - summary_df["utilization_ci95_low"],
            summary_df["utilization_ci95_high"] - summary_df["utilization_mean"],
        ],
        marker="o",
        capsize=5,
    )
    plt.xlabel("Capacidad del reverse proxy")
    plt.ylabel("Utilizacion promedio")
    plt.title("Efecto de la capacidad sobre la utilizacion")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "capacity_sweep_utilization.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    main()