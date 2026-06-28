\# Verificación del modelo



La verificación busca revisar que el simulador esté implementado correctamente y que su comportamiento sea coherente con lo esperado.



\## Pruebas realizadas



| Prueba | Configuración | Resultado esperado | Resultado observado |

|---|---|---|---|

| Validación puntual | λ = 8, μ = 1, c = 10 | Simulación cercana a Erlang B | Se obtuvo error relativo cercano a 0.21% |

| Barrido de carga | c = 10, λ variable | El bloqueo debe aumentar al aumentar λ | Se observó aumento progresivo del bloqueo |

| Escenarios de carga | Usuarios activos fijos, carga variable | Escenarios más exigentes deben generar más rechazo | `evento\_peak` presentó el mayor bloqueo |

| Barrido de capacidad | λ = 11.25, c variable | El bloqueo debe disminuir al aumentar c | Se observó disminución clara del bloqueo |

| Evolución del bloqueo | λ = 11.25, c = 10 | La probabilidad acumulada debe estabilizarse | La curva se estabilizó cerca de 0.27 |



\## Resultado de la verificación



Las pruebas muestran que el simulador presenta un comportamiento coherente con el modelo esperado. Cuando aumenta la carga, aumenta la probabilidad de bloqueo. Cuando aumenta la capacidad, disminuye la probabilidad de bloqueo.



Además, la comparación con Erlang B permite verificar que el núcleo del simulador reproduce correctamente el comportamiento teórico de un sistema M/M/c/c.



Por lo tanto, el modelo queda verificado para los experimentos desarrollados en esta etapa.

