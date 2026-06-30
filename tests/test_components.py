"""Tests de los componentes del dominio."""

import pytest

from proxy_sim.components import Backend, Proxy, Request


def test_request_recien_creado_solo_tiene_id_y_arrival():
    """Los demás campos quedan en None/pending hasta que el request avanza."""
    r = Request(id=1, arrival_time=2.5)
    assert r.id == 1
    assert r.arrival_time == 2.5
    assert r.backend_id is None
    assert r.service_start_time is None
    assert r.completion_time is None
    assert r.status == "pending"


def test_request_status_inicia_en_pending():
    r = Request(id=0, arrival_time=0.0)
    assert r.status == "pending"


def test_backend_nuevo_esta_libre_y_vacio():
    b = Backend(id=0, mu=20.0)
    assert b.id == 0
    assert b.mu == 20.0
    assert not b.busy()
    assert b.qlen() == 0
    assert b.load() == 0
    assert b.in_service is None


def test_backend_load_suma_en_servicio_mas_cola():
    """load() = 1 si hay in_service + largo de la cola."""
    b = Backend(id=0, mu=20.0)
    b.in_service = Request(id=1, arrival_time=0.0)
    b.queue.append(Request(id=2, arrival_time=0.0))
    b.queue.append(Request(id=3, arrival_time=0.0))
    assert b.busy()
    assert b.qlen() == 2
    assert b.load() == 3


def test_backend_sin_tope_de_cola_nunca_esta_lleno():
    b = Backend(id=0, mu=20.0)
    assert b.max_queue_size is None
    assert not b.is_full()
    # aunque le metamos muchos, sigue sin estar lleno
    for i in range(1000):
        b.queue.append(Request(id=i, arrival_time=0.0))
    assert not b.is_full()
    assert b.qlen() == 1000


def test_backend_con_tope_se_llena_al_llegar_al_capacidad():
    b = Backend(id=0, mu=20.0, max_queue_size=2)
    assert not b.is_full()
    b.queue.append(Request(id=1, arrival_time=0.0))
    assert not b.is_full()
    b.queue.append(Request(id=2, arrival_time=0.0))
    assert b.is_full()


# ---------- Proxy ----------


def test_proxy_solo_request_cost():
    p = Proxy(cpu_cost_request=0.001, cpu_cost_response=0.0, cpu_capacity=1.0)
    assert p.cpu_cost_request == 0.001
    assert p.cpu_cost_response == 0.0
    assert p.cpu_capacity == 1.0


def test_proxy_solo_response_cost():
    p = Proxy(cpu_cost_request=0.0, cpu_cost_response=0.002, cpu_capacity=1.0)
    assert p.request_service_time() == 0.0
    assert p.response_service_time() == 0.002


def test_proxy_ambos_costs():
    p = Proxy(cpu_cost_request=0.001, cpu_cost_response=0.002, cpu_capacity=1.0)
    assert p.request_service_time() == 0.001
    assert p.response_service_time() == 0.002


def test_proxy_ambos_costs_en_cero_lanza_error():
    with pytest.raises(ValueError):
        Proxy(cpu_cost_request=0.0, cpu_cost_response=0.0, cpu_capacity=1.0)


def test_proxy_cost_negativo_lanza_error():
    with pytest.raises(ValueError):
        Proxy(cpu_cost_request=-0.001, cpu_cost_response=0.0, cpu_capacity=1.0)
    with pytest.raises(ValueError):
        Proxy(cpu_cost_request=0.0, cpu_cost_response=-0.001, cpu_capacity=1.0)


def test_proxy_capacity_invalida_lanza_error():
    with pytest.raises(ValueError):
        Proxy(cpu_cost_request=0.001, cpu_cost_response=0.0, cpu_capacity=0.0)
    with pytest.raises(ValueError):
        Proxy(cpu_cost_request=0.001, cpu_cost_response=0.0, cpu_capacity=-1.0)


def test_proxy_service_times_es_cost_sobre_capacity():
    p = Proxy(cpu_cost_request=0.005, cpu_cost_response=0.01, cpu_capacity=2.0)
    assert p.request_service_time() == pytest.approx(0.0025)
    assert p.response_service_time() == pytest.approx(0.005)


def test_proxy_inicia_idle_y_vacio():
    p = Proxy(cpu_cost_request=0.001, cpu_cost_response=0.001, cpu_capacity=1.0)
    assert not p.busy()
    assert p.qlen() == 0
    assert p.load() == 0
    assert p.in_service is None
    assert p.busy_time == 0.0


def test_proxy_load_suma_in_service_mas_cola():
    p = Proxy(cpu_cost_request=0.001, cpu_cost_response=0.001, cpu_capacity=1.0)
    p.in_service = Request(id=1, arrival_time=0.0)
    p.queue.append(Request(id=2, arrival_time=0.0))
    p.queue.append(Request(id=3, arrival_time=0.0))
    assert p.busy()
    assert p.qlen() == 2
    assert p.load() == 3


def test_proxy_sin_tope_nunca_esta_lleno():
    p = Proxy(cpu_cost_request=0.001, cpu_cost_response=0.001, cpu_capacity=1.0)
    assert p.max_queue_size is None
    assert not p.is_full()
    for i in range(1000):
        p.queue.append(Request(id=i, arrival_time=0.0))
    assert not p.is_full()


def test_proxy_con_tope_se_llena_al_llegar_al_capacidad():
    p = Proxy(
        cpu_cost_request=0.001, cpu_cost_response=0.001,
        cpu_capacity=1.0, max_queue_size=2,
    )
    assert not p.is_full()
    p.queue.append(Request(id=1, arrival_time=0.0))
    assert not p.is_full()
    p.queue.append(Request(id=2, arrival_time=0.0))
    assert p.is_full()


# ---------- Request extendido ----------


def test_request_recien_creado_no_tiene_timestamps_de_proxy():
    """Los campos nuevos del flujo con proxy inician en None."""
    r = Request(id=1, arrival_time=2.5)
    assert r.proxy_start_time is None
    assert r.dispatch_time is None
    assert r.response_start_time is None
    assert r.backend_done_time is None