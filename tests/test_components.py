"""Tests de los componentes del dominio."""

from proxy_sim.components import Backend, Request


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
    assert b.service_complete_event is None


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