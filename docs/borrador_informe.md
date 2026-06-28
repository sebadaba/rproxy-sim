\# Simulación de eventos discretos para el análisis de un sistema reverse proxy con capacidad finita



\## Resumen



Este trabajo presenta el desarrollo de un simulador de eventos discretos para analizar el comportamiento de un sistema reverse proxy con capacidad finita. El modelo implementado representa el proxy como un sistema de pérdida M/M/c/c, donde las solicitudes llegan de forma aleatoria, son atendidas si existe capacidad disponible y son rechazadas si el sistema se encuentra completamente ocupado.



El objetivo principal es estudiar la relación entre carga de entrada, capacidad del sistema, utilización y probabilidad de bloqueo. Para esto se desarrollaron distintos experimentos: una validación puntual contra Erlang B, un barrido de carga, una comparación de escenarios sintéticos, un barrido de capacidad y una traza de evolución de la probabilidad de bloqueo.



Los resultados muestran que el simulador reproduce correctamente el comportamiento teórico esperado para un sistema M/M/c/c. Además, se observa que la probabilidad de bloqueo aumenta de forma importante al incrementar la carga y disminuye al aumentar la capacidad del reverse proxy.



\## 1. Introducción



Los reverse proxies cumplen un rol importante en sistemas de red modernos, ya que reciben solicitudes de clientes y las redirigen hacia servidores internos o servicios backend. En escenarios de alta demanda, estos sistemas pueden saturarse si la cantidad de solicitudes simultáneas supera su capacidad disponible.



Para estudiar este tipo de comportamiento, la simulación de eventos discretos permite representar la evolución del sistema en el tiempo considerando eventos como llegadas de solicitudes y término de servicios. Este enfoque permite evaluar métricas de desempeño sin necesidad de implementar físicamente una infraestructura completa.



En este proyecto se construyó un simulador DES para analizar un reverse proxy con capacidad finita. La primera versión del modelo se enfoca en estudiar saturación y probabilidad de rechazo, dejando extensiones como múltiples backends, colas finitas o políticas de balanceo para trabajo futuro.



\## 2. Descripción del sistema simulado



El sistema modelado corresponde a un reverse proxy que recibe solicitudes de usuarios. Cada solicitud puede ser aceptada o rechazada dependiendo del estado del sistema al momento de su llegada.



El proxy tiene una capacidad máxima `c`, que representa la cantidad máxima de solicitudes que puede atender simultáneamente. Si una solicitud llega cuando hay menos de `c` solicitudes en servicio, esta es aceptada y permanece en el sistema durante un tiempo de servicio aleatorio. Si la solicitud llega cuando el proxy ya tiene `c` solicitudes activas, se rechaza inmediatamente.



En esta versión no se considera cola de espera. Por lo tanto, el modelo corresponde a un sistema de pérdida.



\## 3. Modelo de simulación



El modelo implementado utiliza simulación de eventos discretos. El estado del sistema cambia solamente cuando ocurre un evento relevante.



Los principales eventos considerados son:



\* llegada de una solicitud;

\* salida o término de servicio de una solicitud.



El estado principal del sistema está dado por la cantidad de solicitudes actualmente en servicio. Además, se registran métricas acumuladas como solicitudes generadas, aceptadas, rechazadas, completadas y utilización del proxy.



Las variables principales del modelo son:



| Variable | Descripción                         |

| -------- | ----------------------------------- |

| `λ`      | Tasa de llegada de solicitudes      |

| `μ`      | Tasa de servicio                    |

| `c`      | Capacidad máxima del reverse proxy  |

| `T`      | Tiempo total de simulación          |

| `busy`   | Solicitudes actualmente en servicio |



Las llegadas se modelan mediante una distribución exponencial con tasa `λ`, mientras que los tiempos de servicio se modelan mediante una distribución exponencial con tasa `μ`.



\## 4. Implementación



El simulador fue implementado en Python. El núcleo del modelo se encuentra en el archivo:



```text

src/rproxy\_sim/des\_loss.py

```



La simulación utiliza una lista de eventos futuros implementada mediante una cola de prioridad. Cada evento tiene asociado un tiempo de ocurrencia y un tipo de evento.



Cuando ocurre una llegada, el simulador evalúa si existe capacidad disponible. Si el proxy no está lleno, la solicitud es aceptada y se agenda su evento de salida. Si el proxy está lleno, la solicitud se cuenta como rechazada.



Las principales métricas calculadas son:



\* número total de solicitudes generadas;

\* número de solicitudes aceptadas;

\* número de solicitudes rechazadas;

\* probabilidad de bloqueo;

\* utilización promedio del proxy;

\* ocupación máxima observada;

\* tiempo medio de servicio.



\## 5. Validación del simulador



Para validar el simulador se utilizó la fórmula de Erlang B, ya que el modelo implementado corresponde a un sistema M/M/c/c. Esta comparación permite revisar si la probabilidad de bloqueo simulada coincide con el resultado teórico esperado.



En la validación puntual se utilizaron los siguientes parámetros:



| Parámetro            | Valor |

| -------------------- | ----- |

| `λ`                  | 8     |

| `μ`                  | 1     |

| `c`                  | 10    |

| Tiempo de simulación | 1000  |

| Réplicas             | 30    |



El bloqueo promedio simulado fue aproximadamente `0.1214`, mientras que el valor teórico de Erlang B fue aproximadamente `0.1217`. El error relativo fue cercano a `0.21%`, lo que indica una alta cercanía entre la simulación y el resultado teórico.



!\[Validación puntual contra Erlang B](../results/validation\_erlang\_b\_plot.png)



\## 6. Validación extendida mediante barrido de carga



Además de validar el simulador en un único punto, se realizó un barrido de carga variando la tasa de llegada `λ` y manteniendo fija la capacidad del sistema.



Se evaluaron los siguientes valores:



```text

λ = 2, 4, 6, 8, 10, 12, 14, 16

```



Los resultados muestran que la curva simulada sigue de forma cercana la curva teórica de Erlang B. A medida que aumenta la tasa de llegada, también aumenta la probabilidad de bloqueo.



!\[Barrido de carga contra Erlang B](../results/load\_sweep\_erlang\_b\_plot.png)



Este resultado refuerza la validación del simulador, ya que la coincidencia no ocurre solamente en un caso puntual, sino también a lo largo de distintos niveles de carga.



\## 7. Comparación de escenarios de carga



Luego de validar el modelo, se evaluaron distintos escenarios sintéticos de carga. En todos los escenarios se mantuvo fija la cantidad de usuarios activos y se modificó la intensidad de tráfico.



Los escenarios evaluados fueron:



| Escenario                     | Descripción general           |

| ----------------------------- | ----------------------------- |

| `residencial\_baja\_carga`      | Escenario de baja demanda     |

| `mixta\_residencial\_comercial` | Escenario intermedio          |

| `campus\_universitario`        | Escenario con mayor actividad |

| `corredor\_metro\_comercial`    | Escenario exigente            |

| `evento\_peak`                 | Escenario de alta demanda     |



Los resultados muestran que, al aumentar la carga efectiva, la probabilidad de bloqueo también aumenta. El escenario `evento\_peak` fue el más crítico, con una probabilidad de bloqueo promedio cercana al `42%`.



!\[Probabilidad de bloqueo por escenario](../results/scenario\_blocking\_probability.png)



También se observa que la utilización del proxy aumenta en los escenarios más exigentes. Sin embargo, una alta utilización no necesariamente implica un buen desempeño, ya que también puede estar asociada a una alta cantidad de solicitudes rechazadas.



!\[Utilización por escenario](../results/scenario\_utilization.png)



\## 8. Evolución de la probabilidad de bloqueo



Para observar el comportamiento interno de la simulación, se generó una traza de la probabilidad de bloqueo acumulada durante una ejecución.



El experimento utilizó una carga exigente con:



| Parámetro            | Valor |

| -------------------- | ----- |

| `λ`                  | 11.25 |

| `μ`                  | 1     |

| `c`                  | 10    |

| Tiempo de simulación | 1000  |



Al comienzo de la simulación se observan fluctuaciones más marcadas, debido a que todavía hay pocas solicitudes procesadas. A medida que aumenta el número de solicitudes, la probabilidad de bloqueo acumulada comienza a estabilizarse alrededor de un valor cercano a `0.27`.



!\[Evolución de la probabilidad de bloqueo](../results/blocking\_trace\_plot.png)



Este resultado permite visualizar que la métrica de bloqueo se estabiliza progresivamente durante la ejecución, lo que entrega mayor confianza sobre el horizonte de simulación utilizado.



\## 9. Barrido de capacidad



Finalmente, se realizó un barrido de capacidad para estudiar cómo cambia la probabilidad de bloqueo al aumentar la cantidad máxima de solicitudes simultáneas que puede atender el reverse proxy.



El experimento utilizó una carga exigente con:



| Parámetro            | Valor |

| -------------------- | ----- |

| `λ`                  | 11.25 |

| `μ`                  | 1     |

| Réplicas             | 30    |

| Tiempo de simulación | 1000  |



Se evaluaron distintas capacidades:



```text

c = 6, 8, 10, 12, 14, 16, 20, 24, 30

```



Los resultados muestran que aumentar la capacidad reduce de forma importante la probabilidad de bloqueo. Con `c = 10`, el bloqueo promedio fue cercano a `26.83%`. Al aumentar la capacidad a `c = 16`, el bloqueo bajó a aproximadamente `4.37%`.



!\[Barrido de capacidad - bloqueo](../results/capacity\_sweep\_blocking\_probability.png)



La menor capacidad evaluada que logró mantener el bloqueo bajo `5%` fue:



```text

c = 16 solicitudes simultáneas

```



!\[Barrido de capacidad - utilización](../results/capacity\_sweep\_utilization.png)



Este resultado sugiere que, para una carga de `λ = 11.25` y `μ = 1`, una capacidad de 16 solicitudes simultáneas entrega un compromiso razonable entre reducción de bloqueo y utilización del sistema.



\## 10. Conclusiones



En este proyecto se desarrolló un simulador de eventos discretos para analizar un sistema reverse proxy con capacidad finita. El modelo implementado permitió estudiar la relación entre carga de entrada, capacidad, utilización y probabilidad de bloqueo.



La validación contra Erlang B mostró que el simulador reproduce correctamente el comportamiento esperado de un sistema M/M/c/c. Tanto la validación puntual como el barrido de carga mostraron una alta cercanía entre los resultados simulados y los valores teóricos.



Los experimentos de escenarios permitieron observar que una capacidad fija de 10 solicitudes simultáneas puede ser suficiente para cargas bajas, pero resulta insuficiente para escenarios de mayor demanda. En particular, el escenario `evento\_peak` presentó una probabilidad de bloqueo cercana al 42%.



El barrido de capacidad permitió estimar que, bajo una carga exigente de `λ = 11.25`, una capacidad de `c = 16` solicitudes simultáneas permite reducir el bloqueo por debajo de 5%.



Como trabajo futuro, se propone extender el modelo para considerar cola finita, múltiples backends, políticas de balanceo de carga y escenarios definidos desde archivos de configuración.



\## Referencias preliminares



\* Material del curso sobre simulación de eventos discretos.

\* Material del curso sobre modelado de entradas.

\* Material del curso sobre validación y verificación.

\* Fórmula de Erlang B para sistemas de pérdida M/M/c/c.



