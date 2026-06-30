# proxy-sim

Simulador de eventos discretos de un reverse proxy con varios backends y
load balancers.

## Estructura

```
rproxy-sim/
├── Makefile             comandos: setup / test / notebook / clean
├── pyproject.toml       metadata y dependencias
├── requirements.txt
├── README.md
├── PLAN.md
├── docs/                documentación adicional
│   └── flow.md          diagrama de flujo del simulador
├── src/proxy_sim/       paquete importable (`from proxy_sim import ...`)
│   ├── __init__.py
│   ├── engine.py        motor DES (heap + event loop)
│   ├── rng.py           generador de numpy sembrado
│   ├── components.py    Request, Backend y Proxy
│   ├── loadbalancers.py RoundRobin, Random
│   └── simulator.py     orquestador M/M/k con proxy CPU opcional
└── tests/
    ├── test_engine.py
    ├── test_components.py
    ├── test_loadbalancers.py
    └── test_simulator.py
```

## Quick start

```bash
make setup      # crea .venv, instala deps + jupyter, registra kernel "proxy-sim"
make test       # corre los tests
make notebook   # abre Jupyter (selecciona el kernel "proxy-sim")
```

Requisitos: Python 3.11+, GNU make.

## Flujo del simulador

Ver [docs/flow.md](docs/flow.md) para el diagrama de las 5 etapas que recorre un request (wait_proxy → service_proxy_request → wait_backend → service_backend → service_proxy_response) y los puntos de reject/timeout.

## Uso rápido

```python
from proxy_sim import Simulator

summary = Simulator(
    arrival_rate=10.0,   # lambda (req/s)
    service_rate=20.0,   # mu por backend (req/s)
    duration=10000.0,    # segundos simulados
    seed=42,
).run()

print(summary["mean_latency"])  # ~0.1s para M/M/1 con rho=0.5
```

Para comparar load balancers con `k=3` backends:

```python
from proxy_sim import Simulator, RoundRobin, Random

params = dict(
    arrival_rate=27, service_rate=10, duration=5000,
    num_backends=3, seed=42,
)

for lb in [RoundRobin(), Random()]:
    s = Simulator(load_balancer=lb, **params).run()
    print(lb, s["p95_latency"])
```

## Tests

`make test` corre 28 tests que cubren:

- ordenamiento y empates del motor DES (`time`, `priority`, `seq`, `end_time`)
- distribuciones de los load balancers (RoundRobin uniforme, Random con seed)
- validación empírica contra M/M/1: `E[latency] ~= 1/(mu - lambda)`
- reproducibilidad con seed fija
- política de rechazo cuando `max_queue_size` se llena

## Notebooks

Tras `make setup`, al abrir Jupyter aparece el kernel **proxy-sim**.
Selecciónalo arriba a la derecha. Si editas archivos en `src/proxy_sim/`,
agrega al inicio del notebook:

```python
%load_ext autoreload
%autoreload 2
```

Para recargar módulos sin reiniciar el kernel.
