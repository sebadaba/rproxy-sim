\# Resultado relevante: barrido de capacidad del reverse proxy



En este experimento se realizó un barrido de capacidad del reverse proxy. La idea fue mantener fija una carga de entrada relativamente exigente y luego ir aumentando la cantidad máxima de solicitudes simultáneas que el proxy puede atender. Con esto se buscaba observar cómo cambia la probabilidad de bloqueo cuando el sistema cuenta con más recursos disponibles.



Para este caso se utilizó una tasa de llegada λ = 11.25 y una tasa de servicio μ = 1.0. Esta carga se eligió porque representa un escenario exigente, similar al caso `corredor\_metro\_comercial`, donde existe una mayor concentración de usuarios y una mayor intensidad de solicitudes. De esta forma, el experimento permite analizar cómo se comporta el sistema cuando está sometido a una demanda alta, pero no necesariamente extrema.



Las capacidades evaluadas fueron:



6, 8, 10, 12, 14, 16, 20, 24 y 30 solicitudes simultáneas.



A partir de los resultados se observa una tendencia clara: cuando la capacidad del reverse proxy aumenta, la probabilidad de bloqueo disminuye. Esto tiene sentido, ya que el sistema dispone de más espacios para atender solicitudes al mismo tiempo, por lo que es menos probable que una nueva solicitud llegue justo cuando todos los recursos están ocupados.



En las capacidades más bajas, el sistema presenta un nivel de saturación bastante alto. Por ejemplo, con capacidad 6, la probabilidad de bloqueo fue superior al 50%, lo que significa que más de la mitad de las solicitudes fueron rechazadas. Con capacidad 8, el rechazo disminuye, pero todavía se mantiene en un nivel alto. Luego, con capacidad 10, la probabilidad de bloqueo promedio fue cercana al 26.83%, lo que confirma que esta configuración no es suficiente para una carga de este nivel.



Al seguir aumentando la capacidad, el sistema comienza a mejorar de forma más notoria. Con capacidad 12, el bloqueo baja a cerca de 16.80%, y con capacidad 14 llega aproximadamente a 9.26%. Aunque estos valores son mejores, todavía pueden considerarse altos si se busca que el reverse proxy mantenga un servicio estable y con bajo rechazo.



El resultado más importante aparece con capacidad 16. En este caso, la probabilidad de bloqueo promedio fue cercana al 4.37%, quedando por debajo del umbral de 5%. Por lo tanto, dentro de las capacidades evaluadas, \*\*c = 16 solicitudes simultáneas\*\* fue la primera configuración que logró mantener el rechazo bajo un nivel razonable.



Para capacidades mayores, como 20, 24 y 30, la probabilidad de bloqueo sigue disminuyendo hasta volverse casi nula. Sin embargo, aumentar demasiado la capacidad también implica que el sistema podría quedar sobredimensionado para esta carga específica. Por eso, el valor c = 16 resulta especialmente relevante, ya que aparece como una capacidad mínima razonable para controlar el bloqueo sin aumentar recursos más de lo necesario.



En resumen, este experimento permite obtener una primera referencia de dimensionamiento del reverse proxy. Para una carga similar al escenario `corredor\_metro\_comercial`, una capacidad de 10 solicitudes simultáneas no alcanza para mantener baja la tasa de rechazo. En cambio, una capacidad de 16 solicitudes simultáneas permite reducir la probabilidad de bloqueo a menos del 5%, lo que la convierte en una opción adecuada dentro de los parámetros evaluados.



