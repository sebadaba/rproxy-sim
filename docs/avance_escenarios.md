\# Avance: Comparación de escenarios de carga para el Reverse Proxy



\## Objetivo del experimento



En esta parte del proyecto se realizó una comparación entre distintos escenarios de carga para ver cómo cambia el comportamiento del reverse proxy cuando aumenta la cantidad de solicitudes que llegan al sistema.



La idea fue mantener fija la cantidad de usuarios activos y también la capacidad del proxy, para que la comparación dependiera principalmente de la intensidad del tráfico generado en cada escenario. Con esto se busca observar desde qué punto el sistema empieza a saturarse y cómo aumenta la probabilidad de rechazo cuando la carga se vuelve más exigente.



\## Configuración general



Para todos los escenarios se trabajó con la misma configuración base:



\* Tiempo de simulación: 1000 unidades de tiempo.

\* Número de réplicas: 30.

\* Usuarios activos considerados: 5000.

\* Tasa de servicio: 1.0.

\* Capacidad del reverse proxy: 10 solicitudes simultáneas.



La tasa efectiva de llegada de solicitudes se calculó considerando la cantidad de usuarios activos, la tasa de solicitudes por usuario y un factor de ráfaga asociado a cada escenario.



La fórmula utilizada fue:



λ = usuarios\_activos × request\_rate\_per\_user × burst\_factor



De esta forma, se pudo representar que algunos escenarios tienen tráfico más bajo y distribuido, mientras que otros concentran una mayor cantidad de solicitudes en menos tiempo.



\## Escenarios evaluados



Se definieron cinco escenarios sintéticos, pensados para representar distintos niveles de concentración de usuarios y actividad de red:



\* `residencial\_baja\_carga`: representa una zona principalmente residencial, donde el tráfico es más distribuido y la intensidad por usuario es baja.

\* `mixta\_residencial\_comercial`: representa una zona donde conviven viviendas y comercio local, por lo que la actividad de red aumenta.

\* `campus\_universitario`: representa un entorno con usuarios más concentrados, donde el tráfico puede ser más sincronizado.

\* `corredor\_metro\_comercial`: representa una zona con mayor movilidad, comercio y concentración de solicitudes.

\* `evento\_peak`: representa una situación de alta demanda temporal, como un horario punta, un evento o un aumento masivo de actividad.



Estos escenarios no buscan ser una medición exacta de una zona real, sino una forma controlada de comparar cómo responde el sistema ante distintos niveles de carga.



\## Resultados principales



Los resultados muestran que, a medida que aumenta la tasa efectiva de llegada, también aumenta la probabilidad de bloqueo y la utilización promedio del reverse proxy.



En el escenario `residencial\_baja\_carga`, la tasa de llegada fue 5.0 y la probabilidad de bloqueo promedio fue cercana a 1.84%. La utilización promedio del proxy fue aproximadamente 48.9%, por lo que el sistema todavía opera con bastante margen.



En el escenario `mixta\_residencial\_comercial`, la tasa de llegada aumentó a 7.2 y la probabilidad de bloqueo promedio subió a 8.68%. La utilización promedio fue cercana a 65.7%, lo que muestra un aumento importante en la ocupación del sistema.



En el escenario `campus\_universitario`, la tasa de llegada fue 8.775 y la probabilidad de bloqueo promedio llegó a 15.84%. La utilización promedio fue aproximadamente 73.9%, indicando que el proxy empieza a trabajar en una zona de mayor presión.



En el escenario `corredor\_metro\_comercial`, la tasa de llegada fue 11.25 y la probabilidad de bloqueo promedio aumentó a 26.98%. La utilización promedio fue cercana a 82.0%, por lo que el sistema ya presenta un nivel considerable de saturación.



Finalmente, en el escenario `evento\_peak`, la tasa de llegada fue 15.3 y la probabilidad de bloqueo promedio alcanzó 42.05%. La utilización promedio fue cercana a 88.7%, mostrando que la capacidad configurada no es suficiente para absorber una carga tan alta sin rechazar una cantidad importante de solicitudes.



\## Interpretación



A partir de los resultados se puede observar que el reverse proxy tiene un buen comportamiento en escenarios de baja carga, pero comienza a rechazar solicitudes de forma más notoria cuando aumenta la intensidad del tráfico.



El escenario residencial presenta una baja tasa de bloqueo, lo que indica que el sistema aún tiene capacidad disponible. En cambio, los escenarios de campus, corredor comercial y evento peak muestran una saturación progresiva, reflejada tanto en la probabilidad de bloqueo como en la utilización promedio del proxy.



El caso `evento\_peak` es el más crítico, ya que muestra que una capacidad de 10 solicitudes simultáneas no alcanza para responder adecuadamente frente a una situación de alta demanda. En ese escenario, una parte importante de las solicitudes termina siendo rechazada.



\## Utilidad para el informe



Este experimento aporta una base útil para la sección de resultados del informe, ya que permite mostrar cómo cambia el rendimiento del sistema bajo distintas condiciones de carga.



También permite justificar la importancia de estudiar la capacidad del reverse proxy. Los resultados muestran que, si la demanda aumenta y la capacidad se mantiene fija, la tasa de rechazo puede crecer rápidamente.



Los gráficos generados ayudan a visualizar principalmente dos aspectos:



\* la probabilidad de bloqueo en cada escenario;

\* la utilización promedio del reverse proxy.



Estos resultados pueden usarse para discutir en qué condiciones el sistema funciona de forma aceptable y en cuáles comienza a saturarse.



\## Archivos generados



Durante este experimento se generaron los siguientes archivos:



\* `results/scenario\_comparison\_replicas.csv`: contiene los resultados obtenidos en cada réplica.

\* `results/scenario\_comparison\_summary.csv`: contiene el resumen estadístico de cada escenario.

\* `results/scenario\_comparison\_summary.txt`: contiene el resumen en formato de texto.

\* `results/scenario\_blocking\_probability.png`: gráfico de la probabilidad de bloqueo por escenario.

\* `results/scenario\_utilization.png`: gráfico de la utilización promedio por escenario.



\## Conclusión preliminar



La comparación realizada muestra que el simulador permite identificar claramente cuándo el reverse proxy empieza a saturarse. Con una capacidad fija de 10 solicitudes simultáneas, el sistema responde bien en escenarios de baja carga, pero presenta una tasa de rechazo cada vez mayor cuando el tráfico se concentra o aumenta la demanda.



Este resultado sirve como punto de partida para los siguientes experimentos, donde será necesario analizar cómo cambia el comportamiento del sistema al modificar la capacidad del proxy.



