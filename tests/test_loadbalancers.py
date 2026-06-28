"""Tests de load balancers."""

from proxy_sim.components import Backend
from proxy_sim.loadbalancers import Random, RoundRobin
from proxy_sim.rng import make_rng


def _backends(k: int) -> list[Backend]:
    return [Backend(id=i, mu=20.0) for i in range(k)]


def test_round_robin_es_determinista_sin_rng():
    """RR no usa el RNG: dos instancias frescas producen la misma secuencia."""
    a = RoundRobin()
    b = RoundRobin()
    bs = _backends(3)
    seq_a = [a.select(bs, None) for _ in range(6)]
    seq_b = [b.select(bs, None) for _ in range(6)]
    assert seq_a == seq_b
    assert seq_a == [0, 1, 2, 0, 1, 2]


def test_round_robin_distribuye_por_igual():
    """N llamadas con k backends → cada uno recibe ~N/k (±5%)."""
    rr = RoundRobin()
    bs = _backends(3)
    counts = [0, 0, 0]
    N = 3000
    for _ in range(N):
        counts[rr.select(bs, None)] += 1
    expected = N / 3
    for c in counts:
        assert abs(c - expected) / expected < 0.05


def test_round_robin_con_un_backend_siempre_devuelve_cero():
    rr = RoundRobin()
    bs = _backends(1)
    for _ in range(5):
        assert rr.select(bs, None) == 0


def test_random_es_determinista_con_mismo_seed():
    rng_a = make_rng(42)
    rng_b = make_rng(42)
    ra, rb = Random(), Random()
    bs = _backends(3)
    seq_a = [ra.select(bs, rng_a) for _ in range(10)]
    seq_b = [rb.select(bs, rng_b) for _ in range(10)]
    assert seq_a == seq_b


def test_random_distribuye_por_igual():
    rng = make_rng(123)
    rand = Random()
    bs = _backends(4)
    counts = [0, 0, 0, 0]
    N = 4000
    for _ in range(N):
        counts[rand.select(bs, rng)] += 1
    expected = N / 4
    for c in counts:
        assert abs(c - expected) / expected < 0.1