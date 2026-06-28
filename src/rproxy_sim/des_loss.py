import heapq
from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class Event:
    time: float
    event_type: str


def erlang_b(offered_load: float, capacity: int) -> float:
    b = 1.0
    for k in range(1, capacity + 1):
        b = (offered_load * b) / (k + offered_load * b)
    return b


def simulate_reverse_proxy(
    arrival_rate: float,
    service_rate: float,
    capacity: int,
    simulation_time: float,
    seed: int = 1234,
) -> Dict[str, float]:

    rng = np.random.default_rng(seed)

    clock = 0.0
    busy = 0

    arrivals = 0
    accepted = 0
    rejected = 0
    completed = 0

    max_busy = 0
    area_busy = 0.0
    last_event_time = 0.0

    service_times: List[float] = []

    fel = []
    event_counter = 0

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

        delta = clock - last_event_time
        area_busy += busy * delta
        last_event_time = clock

        if event.event_type == "arrival":
            arrivals += 1

            next_arrival = clock + rng.exponential(1 / arrival_rate)
            if next_arrival <= simulation_time:
                schedule_event(next_arrival, "arrival")

            if busy < capacity:
                accepted += 1
                busy += 1
                max_busy = max(max_busy, busy)

                service_time = rng.exponential(1 / service_rate)
                service_times.append(service_time)

                departure_time = clock + service_time
                schedule_event(departure_time, "departure")
            else:
                rejected += 1

        elif event.event_type == "departure":
            completed += 1
            busy -= 1

    blocking_probability = rejected / arrivals if arrivals > 0 else 0.0
    utilization = area_busy / (capacity * simulation_time) if capacity > 0 else 0.0
    mean_service_time = float(np.mean(service_times)) if service_times else 0.0

    return {
        "arrivals": arrivals,
        "accepted": accepted,
        "rejected": rejected,
        "completed": completed,
        "blocking_probability": blocking_probability,
        "utilization": utilization,
        "max_busy": max_busy,
        "mean_service_time": mean_service_time,
    }


def run_replicas(
    arrival_rate: float,
    service_rate: float,
    capacity: int,
    simulation_time: float,
    replicas: int = 30,
    seed: int = 1234,
):
    results = []

    for i in range(replicas):
        result = simulate_reverse_proxy(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            capacity=capacity,
            simulation_time=simulation_time,
            seed=seed + i,
        )
        result["replica"] = i + 1
        results.append(result)

    return results


if __name__ == "__main__":
    result = simulate_reverse_proxy(
        arrival_rate=8.0,
        service_rate=1.0,
        capacity=10,
        simulation_time=1000,
        seed=1234,
    )

    theoretical = erlang_b(offered_load=8.0 / 1.0, capacity=10)

    print("Resultados simulacion DES minima")
    print("--------------------------------")
    for key, value in result.items():
        print(f"{key}: {value}")

    print("--------------------------------")
    print(f"Erlang B teorico: {theoretical}")