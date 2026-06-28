import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from rproxy_sim.des_loss import run_replicas, erlang_b


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
    seed = 777

    service_rate = 1.0
    capacity = 10

    arrival_rates = [2, 4, 6, 8, 10, 12, 14, 16]

    all_rows = []

    for arrival_rate in arrival_rates:
        replica_results = run_replicas(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            capacity=capacity,
            simulation_time=simulation_time,
            replicas=replicas,
            seed=seed + int(arrival_rate),
        )

        theoretical = erlang_b(
            offered_load=arrival_rate / service_rate,
            capacity=capacity,
        )

        for row in replica_results:
            row["arrival_rate"] = arrival_rate
            row["service_rate"] = service_rate
            row["capacity"] = capacity
            row["erlang_b_theoretical"] = theoretical
            all_rows.append(row)

    df = pd.DataFrame(all_rows)

    summary_rows = []

    for arrival_rate, group in df.groupby("arrival_rate"):
        bp_mean, bp_low, bp_high = confidence_interval_95(group["blocking_probability"])

        theoretical = group["erlang_b_theoretical"].iloc[0]
        relative_error = abs(bp_mean - theoretical) / theoretical if theoretical > 0 else 0.0

        summary_rows.append(
            {
                "arrival_rate": arrival_rate,
                "service_rate": service_rate,
                "capacity": capacity,
                "blocking_probability_mean": bp_mean,
                "blocking_probability_ci95_low": bp_low,
                "blocking_probability_ci95_high": bp_high,
                "erlang_b_theoretical": theoretical,
                "relative_error": relative_error,
                "mean_rejected": group["rejected"].mean(),
                "mean_accepted": group["accepted"].mean(),
                "mean_arrivals": group["arrivals"].mean(),
            }
        )

    summary_df = pd.DataFrame(summary_rows).sort_values("arrival_rate")

    csv_path = results_dir / "load_sweep_erlang_b_replicas.csv"
    summary_csv_path = results_dir / "load_sweep_erlang_b_summary.csv"
    txt_path = results_dir / "load_sweep_erlang_b_summary.txt"

    df.to_csv(csv_path, index=False)
    summary_df.to_csv(summary_csv_path, index=False)

    txt = "Barrido de carga contra Erlang B\n"
    txt += "================================\n\n"
    txt += f"simulation_time = {simulation_time}\n"
    txt += f"replicas = {replicas}\n"
    txt += f"service_rate = {service_rate}\n"
    txt += f"capacity = {capacity}\n"
    txt += f"arrival_rates = {arrival_rates}\n\n"
    txt += summary_df.to_string(index=False)
    txt += "\n"

    txt_path.write_text(txt, encoding="utf-8")

    print(txt)

    plt.figure()
    plt.errorbar(
        summary_df["arrival_rate"],
        summary_df["blocking_probability_mean"],
        yerr=[
            summary_df["blocking_probability_mean"] - summary_df["blocking_probability_ci95_low"],
            summary_df["blocking_probability_ci95_high"] - summary_df["blocking_probability_mean"],
        ],
        marker="o",
        capsize=5,
        label="Simulacion",
    )

    plt.plot(
        summary_df["arrival_rate"],
        summary_df["erlang_b_theoretical"],
        marker="s",
        linestyle="--",
        label="Erlang B teorico",
    )

    plt.xlabel("Tasa de llegada λ")
    plt.ylabel("Probabilidad de bloqueo")
    plt.title("Validacion del simulador para distintas cargas")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "load_sweep_erlang_b_plot.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    main()