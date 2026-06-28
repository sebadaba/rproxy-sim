import heapq
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


@dataclass
class Event:
    time: float
    event_type: str


def simulate_blocking_trace(
    arrival_rate: float,
    service_rate: float,
    capacity: int,
    simulation_time: float,
    seed: int = 1234,
    sample_every: int = 250,
):
    rng = np.random.default_rng(seed)

    clock = 0.0
    busy = 0

    arrivals = 0
    accepted = 0
    rejected = 0
    completed = 0

    fel = []
    event_counter = 0
    trace = []

    def schedule_event(time: float, event_type: str):
        nonlocal event_counter
        event_counter += 1
        heapq.heappush(fel, (time, event_counter, Event(time, event_type)))

    first_arrival = rng.exponential(1 / arrival_rate)
    schedule_event(first_arrival, "arrival")

    while fel:
        event_time, _, event = heapq.heappop(fel)

        if event_time > simulation_time:
            break

        clock = event_time

        if event.event_type == "arrival":
            arrivals += 1

            next_arrival = clock + rng.exponential(1 / arrival_rate)
            if next_arrival <= simulation_time:
                schedule_event(next_arrival, "arrival")

            if busy < capacity:
                accepted += 1
                busy += 1
                service_time = rng.exponential(1 / service_rate)
                schedule_event(clock + service_time, "departure")
            else:
                rejected += 1

            if arrivals % sample_every == 0:
                blocking_probability = rejected / arrivals if arrivals > 0 else 0.0
                trace.append(
                    {
                        "clock": clock,
                        "arrivals": arrivals,
                        "accepted": accepted,
                        "rejected": rejected,
                        "completed": completed,
                        "busy": busy,
                        "blocking_probability": blocking_probability,
                    }
                )

        elif event.event_type == "departure":
            completed += 1
            busy -= 1

    final_blocking = rejected / arrivals if arrivals > 0 else 0.0

    trace.append(
        {
            "clock": clock,
            "arrivals": arrivals,
            "accepted": accepted,
            "rejected": rejected,
            "completed": completed,
            "busy": busy,
            "blocking_probability": final_blocking,
        }
    )

    return pd.DataFrame(trace)


def main():
    arrival_rate = 11.25
    service_rate = 1.0
    capacity = 10
    simulation_time = 1000
    seed = 2026

    df = simulate_blocking_trace(
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        capacity=capacity,
        simulation_time=simulation_time,
        seed=seed,
        sample_every=250,
    )

    csv_path = RESULTS / "blocking_trace.csv"
    plot_path = RESULTS / "blocking_trace_plot.png"
    summary_path = RESULTS / "blocking_trace_summary.txt"

    df.to_csv(csv_path, index=False)

    final_blocking = df["blocking_probability"].iloc[-1]

    summary = f"""
Evolucion de probabilidad de bloqueo
====================================

arrival_rate = {arrival_rate}
service_rate = {service_rate}
capacity = {capacity}
simulation_time = {simulation_time}
seed = {seed}

bloqueo_final = {final_blocking}

Archivos generados:
{csv_path}
{plot_path}
"""

    summary_path.write_text(summary, encoding="utf-8")

    print(summary)

    plt.figure()
    plt.plot(df["arrivals"], df["blocking_probability"], marker="o")
    plt.xlabel("Solicitudes generadas")
    plt.ylabel("Probabilidad de bloqueo acumulada")
    plt.title("Evolucion de la probabilidad de bloqueo durante la simulacion")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300)
    plt.close()


if __name__ == "__main__":
    main()