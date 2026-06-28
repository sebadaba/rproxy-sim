\# Resultado relevante: barrido de carga contra Erlang B



En este experimento se realizó un barrido de carga para validar el comportamiento del simulador frente a distintos niveles de demanda. A diferencia de la primera validación, donde solo se comparó un caso puntual contra Erlang B, aquí se evaluaron varias tasas de llegada manteniendo fija la capacidad del sistema.



Los parámetros utilizados fueron:



\* Tasa de servicio: μ = 1.0.

\* Capacidad del reverse proxy: c = 10.

\* Tiempo de simulación: 1000 unidades de tiempo.

\* Número de réplicas: 30.

\* Tasas de llegada evaluadas: λ = 2, 4, 6, 8, 10, 12, 14 y 16.



El objetivo fue comparar, para cada valor de λ, la probabilidad de bloqueo promedio obtenida mediante simulación con el valor teórico entregado por Erlang B.



Los resultados muestran que la simulación sigue de forma muy cercana la tendencia teórica. A medida que aumenta la tasa de llegada, la probabilidad de bloqueo también aumenta. Esto es consistente con el comportamiento esperado: si llegan más solicitudes al sistema y la capacidad se mantiene fija, es más probable que el reverse proxy se encuentre saturado y rechace nuevas solicitudes.



Para λ = 6, el bloqueo simulado fue aproximadamente 4.31%, prácticamente igual al valor teórico de Erlang B. Para λ = 8, el bloqueo simulado fue cercano a 12.06%, mientras que Erlang B entregó aproximadamente 12.17%. Para λ = 10, la simulación entregó un bloqueo cercano a 21.62%, muy próximo al valor teórico de 21.46%.



En cargas más altas, como λ = 12, 14 y 16, la cercanía también se mantiene. Por ejemplo, para λ = 16, el bloqueo simulado fue aproximadamente 43.86%, mientras que Erlang B entregó cerca de 44.06%.



El caso λ = 2 presenta un error relativo más alto, pero esto se debe a que la probabilidad de bloqueo teórica es extremadamente pequeña. En términos absolutos, la diferencia entre simulación y teoría sigue siendo muy baja, por lo que no representa un problema relevante para la validación.



En general, este experimento refuerza la validez del simulador, ya que muestra que no solo coincide con Erlang B en un punto específico, sino que reproduce correctamente la tendencia completa de aumento del bloqueo al incrementar la carga ofrecida.



Este resultado es útil para el informe porque permite defender mejor el modelo implementado antes de usarlo en escenarios más aplicados, como la comparación de topologías o el análisis de capacidad del reverse proxy.

