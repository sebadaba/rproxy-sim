"""Tests del motor DES."""

from proxy_sim.engine import EventLoop


def test_eventos_se_ejecutan_en_orden_cronologico():
    loop = EventLoop(end_time=100.0)
    orden = []
    loop.schedule(10.0, lambda: orden.append("b"))
    loop.schedule(5.0, lambda: orden.append("a"))
    loop.schedule(20.0, lambda: orden.append("c"))
    loop.run()
    assert orden == ["a", "b", "c"]


def test_priority_desempata_en_mismo_tiempo():
    """priority=0 (SERVICE_COMPLETE) corre antes que priority>0 (ARRIVAL)."""
    loop = EventLoop(end_time=100.0)
    orden = []
    loop.schedule(5.0, lambda: orden.append("arrival"), priority=1)
    loop.schedule(5.0, lambda: orden.append("service_complete"), priority=0)
    loop.run()
    assert orden == ["service_complete", "arrival"]


def test_seq_desempata_en_mismo_tiempo_y_priority():
    """Si time y priority empatan, gana FIFO (orden de inserción)."""
    loop = EventLoop(end_time=100.0)
    orden = []
    loop.schedule(5.0, lambda: orden.append("primero"))
    loop.schedule(5.0, lambda: orden.append("segundo"))
    loop.schedule(5.0, lambda: orden.append("tercero"))
    loop.run()
    assert orden == ["primero", "segundo", "tercero"]


def test_end_time_evento_en_el_borde_si_corre():
    """Un evento agendado exactamente en end_time sí se ejecuta."""
    loop = EventLoop(end_time=10.0)
    fired = []
    loop.schedule(10.0, lambda: fired.append("borde"))
    loop.schedule(15.0, lambda: fired.append("pasado"))
    loop.schedule(5.0, lambda: fired.append("antes"))
    loop.run()
    assert fired == ["antes", "borde"]
    assert loop.now == 10.0
    assert not loop.is_empty()  # el evento de t=15 queda pendiente


def test_agendar_en_el_pasado_lanza_error():
    loop = EventLoop(end_time=10.0)
    loop.now = 5.0
    try:
        loop.schedule(3.0, lambda: None)
    except ValueError:
        pass
    else:
        raise AssertionError("se esperaba ValueError")


def test_now_avanza_al_timestamp_del_evento():
    loop = EventLoop(end_time=100.0)
    marcas = []
    loop.schedule(7.5, lambda: marcas.append(loop.now))
    loop.schedule(2.0, lambda: marcas.append(loop.now))
    loop.run()
    assert marcas == [2.0, 7.5]


def test_loop_vacio_termina_sin_error():
    loop = EventLoop(end_time=10.0)
    loop.run()
    assert loop.now == 0.0
    assert loop.is_empty()


def test_payload_puede_reagendar_eventos():
    """Un payload puede programar nuevos eventos antes de retornar."""
    loop = EventLoop(end_time=100.0)
    contador = [0]

    def explotar():
        contador[0] += 1
        if contador[0] < 3:
            loop.schedule(loop.now + 1.0, explotar)

    loop.schedule(1.0, explotar)
    loop.run()
    assert contador[0] == 3
    assert loop.now == 3.0


def test_schedule_retorna_event_para_referencia():
    """El Event retornado sirve para inspección o cancelación lógica futura."""
    loop = EventLoop(end_time=100.0)
    ev = loop.schedule(5.0, lambda: None)
    assert ev.time == 5.0
    assert ev.priority == 0
    assert ev.seq == 0
    assert loop.peek_next_time() == 5.0