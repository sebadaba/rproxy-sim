# rproxy-sim

Simulador de eventos discretos para analizar el comportamiento de un **reverse proxy** con capacidad finita.

La idea del proyecto es estudiar qué pasa cuando llegan solicitudes al proxy bajo distintas condiciones de carga: cuántas se aceptan, cuántas se rechazan, qué tan utilizado queda el sistema y en qué punto empieza a saturarse.

En esta versión inicial, el sistema se modela como un sistema de pérdida **M/M/c/c**. Es decir, el proxy puede atender hasta `c` solicitudes simultáneas. Si llega una nueva solicitud y todavía hay capacidad disponible, se acepta. Si el sistema ya está lleno, la solicitud se rechaza. Por ahora no se considera cola de espera.

## Estructura del proyecto

```text
rproxy-sim/
├── README.md
├── requirements.txt
│
├── src/
│   └── rproxy_sim/
│       ├── __init__.py
│       └── des_loss.py
│
├── experiments/
│   ├── validation_erlang_b.py
│   ├── load_sweep_erlang_b.py
│   ├── scenario_comparison.py
│   ├── capacity_sweep.py
│   └── blocking_trace.py
│
├── results/
│   ├── *.csv
│   ├── *.txt
│   └── *.png
│
├── notebooks/
│   └── 01_resultados_base.ipynb
│
├── docs/
│   ├── avance_des_minimo.md
│   ├── avance_escenarios.md
│   ├── resultado_capacity_sweep.md
│   ├── resultado_load_sweep_erlang_b.md
│   ├── supuestos_modelo.md
│   └── verificacion_modelo.md
│
└── scenarios/
    └── base.yaml
```

## Instalación

Se recomienda usar Python 3.11 o superior y trabajar dentro de un entorno virtual.

Desde la raíz del repositorio:

```cmd
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

## Uso rápido

Para correr una simulación base:

```cmd
py src\rproxy_sim\des_loss.py
```

Esto ejecuta el modelo DES mínimo y muestra por consola métricas como:

* solicitudes generadas;
* solicitudes aceptadas;
* solicitudes rechazadas;
* probabilidad de bloqueo;
* utilización del proxy;
* ocupación máxima.

## Experimentos

Los experimentos principales están en la carpeta `experiments/`. Cada script genera sus salidas en `results/`, normalmente como archivos `.csv`, `.txt` y gráficos `.png`.

### Validación puntual contra Erlang B

```cmd
py experiments\validation_erlang_b.py
```

Ejecuta una validación simple del simulador comparando la probabilidad de bloqueo simulada con el valor teórico de Erlang B para un sistema M/M/c/c.

### Barrido de carga contra Erlang B

```cmd
py experiments\load_sweep_erlang_b.py
```

Evalúa varias tasas de llegada `λ` manteniendo fija la capacidad del proxy. La idea es comparar la curva simulada de bloqueo contra la curva teórica de Erlang B.

### Comparación de escenarios de carga

```cmd
py experiments\scenario_comparison.py
```

Compara distintos escenarios sintéticos de demanda. En todos los casos se mantiene fija la cantidad de usuarios activos, pero cambia la intensidad del tráfico.

Escenarios incluidos:

* `residencial_baja_carga`
* `mixta_residencial_comercial`
* `campus_universitario`
* `corredor_metro_comercial`
* `evento_peak`

### Barrido de capacidad

```cmd
py experiments\capacity_sweep.py
```

Prueba distintas capacidades máximas del reverse proxy para ver cómo cambia la probabilidad de bloqueo. Este experimento sirve para estimar qué capacidad mínima sería razonable bajo una carga exigente.

### Evolución de la probabilidad de bloqueo

```cmd
py experiments\blocking_trace.py
```

Genera una traza de la probabilidad de bloqueo acumulada durante una simulación. Esto permite ver cómo la métrica se va estabilizando a medida que se procesan más solicitudes.

## Notebook principal

El notebook con el análisis integrado está en:

```text
notebooks/01_resultados_base.ipynb
```

Para abrirlo:

```cmd
jupyter lab
```

Luego entrar a la carpeta `notebooks/` y abrir `01_resultados_base.ipynb`.

El notebook reúne:

* descripción del modelo base;
* validación puntual contra Erlang B;
* validación extendida con barrido de carga;
* comparación de escenarios de carga;
* evolución de la probabilidad de bloqueo;
* barrido de capacidad;
* conclusiones preliminares.

## Resultados obtenidos

En la validación puntual, usando `λ = 8`, `μ = 1` y `c = 10`, el simulador obtuvo una probabilidad de bloqueo promedio cercana a `0.1214`. El valor teórico entregado por Erlang B fue aproximadamente `0.1217`, con un error relativo cercano a `0.21%`.

En el barrido de carga, la simulación siguió de forma cercana la tendencia teórica de Erlang B: al aumentar la tasa de llegada, también aumentó la probabilidad de bloqueo.

En la comparación de escenarios, el caso más exigente fue `evento_peak`, con una probabilidad de bloqueo promedio cercana al `42%`. Esto muestra que una capacidad fija de 10 solicitudes simultáneas no es suficiente para escenarios de alta demanda.

En el barrido de capacidad, para una carga de `λ = 11.25` y `μ = 1.0`, la menor capacidad evaluada que permitió mantener el bloqueo bajo `5%` fue:

```text
c = 16 solicitudes simultáneas
```

Con esa configuración, la probabilidad de bloqueo promedio fue cercana a `4.37%`.

## Supuestos del modelo

El modelo actual trabaja con los siguientes supuestos:

* las llegadas de solicitudes siguen una distribución exponencial;
* los tiempos de servicio siguen una distribución exponencial;
* el proxy tiene capacidad finita;
* no existe cola de espera en esta versión;
* una solicitud se rechaza si llega cuando el proxy está lleno;
* los escenarios usados son sintéticos y sirven para comparar condiciones de carga;
* los resultados se estiman usando múltiples réplicas.

## Estado actual

El proyecto ya cuenta con una base funcional para el análisis del sistema:

* simulador DES mínimo;
* validación contra Erlang B;
* experimentos de carga;
* experimento de capacidad;
* trazas de evolución del bloqueo;
* notebook con resultados integrados.

Con esto se tiene una base suficiente para redactar el informe, especialmente las secciones de modelo DES, implementación, validación, resultados y conclusiones.

## Trabajo futuro

Algunas extensiones posibles para una versión posterior son:

* agregar cola finita y pasar a un modelo tipo M/M/c/K;
* modelar múltiples backends;
* implementar políticas de balanceo como Round Robin o Random;
* agregar tests automáticos;
* crear una interfaz interactiva con Streamlit;
* leer escenarios directamente desde archivos YAML.

