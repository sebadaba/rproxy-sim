\# Supuestos del modelo



El modelo implementado representa un sistema reverse proxy con capacidad finita. Para esta primera versión se realizaron algunos supuestos que permiten mantener el modelo simple y validable.



\## Supuestos principales



| Elemento | Supuesto adoptado | Justificación |

|---|---|---|

| Llegadas de solicitudes | Las llegadas siguen una distribución exponencial con tasa λ | Permite modelar llegadas aleatorias y validar el sistema con Erlang B |

| Tiempos de servicio | Los tiempos de servicio siguen una distribución exponencial con tasa μ | Permite representar variabilidad en la atención de solicitudes |

| Capacidad del proxy | El proxy puede atender hasta c solicitudes simultáneas | Representa un límite físico o lógico del sistema |

| Cola de espera | No se considera cola en la versión base | Se modela un sistema de pérdida M/M/c/c |

| Solicitudes rechazadas | Una solicitud se rechaza si llega cuando el proxy está lleno | Permite medir probabilidad de bloqueo |

| Usuarios activos | Se usan 5000 usuarios activos en los escenarios sintéticos | Permite comparar escenarios manteniendo fija la población activa |

| Réplicas | Se utilizan 30 réplicas por experimento | Permite estimar promedios e intervalos de confianza |

| Condición de término | La simulación termina al alcanzar un tiempo fijo T | Facilita comparar experimentos bajo el mismo horizonte temporal |



\## Alcance del modelo



El modelo no busca representar todos los detalles internos de un reverse proxy real. En esta etapa se enfoca en estudiar la relación entre carga de entrada, capacidad del sistema, utilización y probabilidad de bloqueo.



Esto permite analizar saturación y dimensionamiento de forma controlada antes de extender el simulador a modelos más complejos.

