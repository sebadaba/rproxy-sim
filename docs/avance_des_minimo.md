\# Avance: Simulador DES mínimo para Reverse Proxy



\## Objetivo del avance



En esta primera etapa se implementó un simulador básico de eventos discretos para representar el funcionamiento de un reverse proxy con capacidad limitada. La idea principal fue modelar cómo llegan solicitudes al sistema, cuánto tiempo permanecen siendo atendidas y qué ocurre cuando el proxy ya no tiene recursos disponibles.



Este primer avance funciona como una base inicial del proyecto, ya que permite tener un núcleo de simulación simple, pero útil, sobre el cual después se podrán agregar escenarios más específicos, como cambios en la carga de usuarios, distintas capacidades del proxy y comparaciones entre topologías.



\## Modelo implementado



Para esta versión inicial, el reverse proxy fue representado como un sistema de pérdida M/M/c/c. Esto significa que el sistema tiene una cantidad limitada de espacios disponibles para atender solicitudes y no considera una cola de espera.



En particular, se asumió lo siguiente:



\* Las llegadas de solicitudes se modelan mediante una distribución exponencial con tasa λ.

\* Los tiempos de servicio se modelan mediante una distribución exponencial con tasa μ.

\* La capacidad máxima del proxy está dada por el parámetro c.

\* En esta primera versión no se considera cola.

\* Si una solicitud llega cuando el proxy está completamente ocupado, esta se rechaza.

\* Si existe capacidad disponible, la solicitud es aceptada y se agenda su evento de salida.



Este modelo permite estudiar de forma directa la saturación del reverse proxy y la probabilidad de rechazo de solicitudes bajo distintas condiciones de carga.



\## Elementos DES considerados



El simulador incorpora los componentes principales de una simulación de eventos discretos:



\* Estado del sistema: se considera el reloj de simulación y la cantidad de solicitudes que están siendo atendidas en cada instante.

\* Entidades: las solicitudes que llegan al reverse proxy.

\* Eventos: llegada de una solicitud y salida de una solicitud.

\* FEL: la lista de eventos futuros se maneja como una cola de prioridad ordenada por tiempo.

\* Condición de término: la simulación termina cuando se alcanza un tiempo máximo definido.

\* Estadísticas: se registran solicitudes generadas, aceptadas, rechazadas, completadas, utilización del proxy, ocupación máxima y tiempo medio de servicio.



Con esto se tiene una estructura mínima, pero suficiente, para representar el comportamiento temporal del sistema y obtener métricas de rendimiento.



\## Parámetros usados en la validación



Para validar esta primera versión del simulador se utilizaron los siguientes parámetros:



\* arrival\_rate = 8.0

\* service\_rate = 1.0

\* capacity = 10

\* simulation\_time = 1000

\* replicas = 30



Estos valores permiten comparar el resultado de la simulación con el valor teórico de Erlang B, ya que el modelo usado corresponde a un sistema M/M/c/c.



\## Resultados obtenidos



Al ejecutar 30 réplicas de la simulación se obtuvieron los siguientes resultados:



\* Probabilidad de bloqueo promedio simulada: 0.12140635415015041

\* Desviación estándar: 0.006189497411669924

\* Intervalo de confianza al 95%: \[0.11919147094684933, 0.1236212373534515]

\* Valor teórico de Erlang B: 0.1216610642529515

\* Error relativo: 0.0020936040989376187



\## Interpretación de los resultados



Los resultados muestran que la probabilidad de bloqueo obtenida mediante simulación es muy cercana al valor teórico calculado con Erlang B. El error relativo fue cercano a 0.21%, por lo que la diferencia entre ambos valores es bastante baja.



Además, el valor teórico de Erlang B queda dentro del intervalo de confianza al 95% obtenido con las réplicas. Esto entrega una primera evidencia de que el simulador está funcionando de forma correcta para este caso base.



En otras palabras, antes de avanzar hacia escenarios más complejos, se pudo comprobar que el núcleo del simulador reproduce adecuadamente el comportamiento esperado para un sistema con capacidad finita y sin cola.



\## Archivos generados



Durante este avance se generaron los siguientes archivos:



\* `src/rproxy\_sim/des\_loss.py`: contiene la implementación del simulador DES mínimo.

\* `experiments/validation\_erlang\_b.py`: ejecuta el experimento de validación contra Erlang B.

\* `results/validation\_erlang\_b\_replicas.csv`: guarda los resultados de las 30 réplicas.

\* `results/validation\_erlang\_b\_summary.txt`: guarda el resumen numérico de la validación.

\* `results/validation\_erlang\_b\_plot.png`: contiene el gráfico generado para la validación.



\## Relación con el informe



Este avance se puede incorporar directamente en varias secciones del informe final.



\### Modelo de Simulación de Eventos Discretos



Permite explicar cuáles son las variables de estado, las entidades, los eventos considerados, la lista de eventos futuros, la condición de término y el funcionamiento general del avance del reloj de simulación.



\### Implementación



Permite justificar que el simulador fue implementado en Python y que la FEL se maneja mediante una cola de prioridad, lo que permite procesar los eventos en orden cronológico.



\### Resultados y validación



Sirve como primera validación del simulador, ya que compara la probabilidad de bloqueo simulada con el resultado teórico de Erlang B. Además, incluye réplicas, intervalo de confianza y error relativo.



\### Conclusión preliminar



El modelo base queda validado para un escenario simple de tipo M/M/c/c. A partir de esta implementación ya es posible avanzar hacia experimentos más representativos del proyecto, como modificar la carga de entrada, variar la capacidad del reverse proxy y comparar escenarios asociados a distintas topologías o condiciones de usuarios.



