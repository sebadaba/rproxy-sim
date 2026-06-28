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
    seed = 2026

    fixed_active_users = 5000
    service_rate = 1.0
    proxy_capacity = 10

    scenarios = [
        {
            "scenario": "residencial_baja_carga",
            "description": "Zona residencial con trafico distribuido y baja intensidad por usuario.",
            "active_users": fixed_active_users,
            "request_rate_per_user": 0.0010,
            "burst_factor": 1.0,
        },
        {
            "scenario": "mixta_residencial_comercial",
            "description": "Zona mixta con viviendas, comercio local y mayor actividad durante horarios punta.",
            "active_users": fixed_active_users,
            "request_rate_per_user": 0.0012,
            "burst_factor": 1.2,
        },
        {
            "scenario": "campus_universitario",
            "description": "Escenario tipo campus con usuarios concentrados y trafico mas sincronizado.",
            "active_users": fixed_active_users,
            "request_rate_per_user": 0.0013,
            "burst_factor": 1.35,
        },
        {
            "scenario": "corredor_metro_comercial",
            "description": "Sector con alta movilidad, comercio y mayor concentracion de solicitudes.",
            "active_users": fixed_active_users,
            "request_rate_per_user": 0.0015,
            "burst_factor": 1.5,
        },
        {
            "scenario": "evento_peak",
            "description": "Escenario de sobrecarga temporal por evento, horario punta o comportamiento masivo.",
            "active_users": fixed_active_users,
            "request_rate_per_user": 0.0017,
            "burst_factor": 1.8,
        },
    ]

    all_rows = []

    for scenario in scenarios:
        arrival_rate = (
            scenario["active_users"]
            * scenario["request_rate_per_user"]
            * scenario["burst_factor"]
        )

        replica_results = run_replicas(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            capacity=proxy_capacity,
            simulation_time=simulation_time,
            replicas=replicas,
            seed=seed,
        )

        for row in replica_results:
            row["scenario"] = scenario["scenario"]
            row["description"] = scenario["description"]
            row["active_users"] = scenario["active_users"]
            row["request_rate_per_user"] = scenario["request_rate_per_user"]
            row["burst_factor"] = scenario["burst_factor"]
            row["arrival_rate"] = arrival_rate
            row["service_rate"] = service_rate
            row["proxy_capacity"] = proxy_capacity
            all_rows.append(row)

    df = pd.DataFrame(all_rows)

    summary_rows = []

    for scenario_name, group in df.groupby("scenario"):
        bp_mean, bp_low, bp_high = confidence_interval_95(group["blocking_probability"])
        util_mean, util_low, util_high = confidence_interval_95(group["utilization"])

        summary_rows.append(
            {
                "scenario": scenario_name,
                "arrival_rate": group["arrival_rate"].iloc[0],
                "active_users": group["active_users"].iloc[0],
                "request_rate_per_user": group["request_rate_per_user"].iloc[0],
                "burst_factor": group["burst_factor"].iloc[0],
                "proxy_capacity": group["proxy_capacity"].iloc[0],
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

    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df.sort_values("arrival_rate")

    csv_path = results_dir / "scenario_comparison_replicas.csv"
    summary_csv_path = results_dir / "scenario_comparison_summary.csv"
    txt_path = results_dir / "scenario_comparison_summary.txt"

    df.to_csv(csv_path, index=False)
    summary_df.to_csv(summary_csv_path, index=False)

    txt = "Comparacion de escenarios - Reverse Proxy DES\n"
    txt += "============================================\n\n"
    txt += f"simulation_time = {simulation_time}\n"
    txt += f"replicas = {replicas}\n"
    txt += f"usuarios_activos_fijos = {fixed_active_users}\n"
    txt += f"service_rate = {service_rate}\n"
    txt += f"proxy_capacity = {proxy_capacity}\n\n"
    txt += summary_df.to_string(index=False)

    txt_path.write_text(txt, encoding="utf-8")

    print(txt)

    plt.figure()
    plt.errorbar(
        summary_df["scenario"],
        summary_df["blocking_probability_mean"],
        yerr=[
            summary_df["blocking_probability_mean"] - summary_df["blocking_probability_ci95_low"],
            summary_df["blocking_probability_ci95_high"] - summary_df["blocking_probability_mean"],
        ],
        marker="o",
        capsize=5,
    )
    plt.xlabel("Escenario")
    plt.ylabel("Probabilidad de bloqueo")
    plt.title("Probabilidad de bloqueo por escenario")
    plt.xticks(rotation=30, ha="right")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "scenario_blocking_probability.png", dpi=300)
    plt.close()

    plt.figure()
    plt.errorbar(
        summary_df["scenario"],
        summary_df["utilization_mean"],
        yerr=[
            summary_df["utilization_mean"] - summary_df["utilization_ci95_low"],
            summary_df["utilization_ci95_high"] - summary_df["utilization_mean"],
        ],
        marker="o",
        capsize=5,
    )
    plt.xlabel("Escenario")
    plt.ylabel("Utilizacion promedio")
    plt.title("Utilizacion del reverse proxy por escenario")
    plt.xticks(rotation=30, ha="right")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "scenario_utilization.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    main()