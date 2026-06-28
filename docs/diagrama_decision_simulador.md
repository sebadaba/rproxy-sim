\# Diagrama de decisión del simulador DES



Este diagrama representa el flujo principal de decisiones del simulador de eventos discretos implementado para el reverse proxy.



```mermaid

flowchart TD

&#x20;   A(\[Inicio de simulación]) --> B\[Recibir parámetros de entrada]

&#x20;   B --> B1\[Parámetros: λ, μ, capacidad c, tiempo T, seed]

&#x20;   B1 --> C\[Inicializar generador aleatorio con seed]



&#x20;   C --> D\[Inicializar variables de estado]

&#x20;   D --> D1\[clock = 0]

&#x20;   D1 --> D2\[busy = 0]

&#x20;   D2 --> D3\[max\_busy = 0]

&#x20;   D3 --> D4\[area\_busy = 0]



&#x20;   D4 --> E\[Inicializar contadores]

&#x20;   E --> E1\[arrivals = 0]

&#x20;   E1 --> E2\[accepted = 0]

&#x20;   E2 --> E3\[rejected = 0]

&#x20;   E3 --> E4\[completed = 0]



&#x20;   E4 --> F\[Crear FEL: lista de eventos futuros]

&#x20;   F --> G\[Generar tiempo de primera llegada]

&#x20;   G --> H\[Agendar primer evento arrival en la FEL]



&#x20;   H --> I{¿FEL vacía?}



&#x20;   I -- Sí --> Z\[Calcular métricas finales]

&#x20;   I -- No --> J\[Extraer evento más próximo de la FEL]



&#x20;   J --> K{¿event\_time > T?}

&#x20;   K -- Sí --> Z

&#x20;   K -- No --> L\[Actualizar estadísticas acumuladas]



&#x20;   L --> L1\[area\_busy += busy \* diferencia de tiempo]

&#x20;   L1 --> L2\[clock = event\_time]



&#x20;   L2 --> M{¿Tipo de evento?}



&#x20;   M -- arrival --> N\[Procesar llegada]

&#x20;   N --> N1\[arrivals += 1]

&#x20;   N1 --> N2\[Generar próxima llegada]

&#x20;   N2 --> N3{¿next\_arrival <= T?}



&#x20;   N3 -- Sí --> N4\[Agendar nuevo evento arrival]

&#x20;   N3 -- No --> N5\[No se agenda otra llegada]

&#x20;   N4 --> O{¿busy < capacity?}

&#x20;   N5 --> O



&#x20;   O -- Sí --> P\[Aceptar solicitud]

&#x20;   P --> P1\[accepted += 1]

&#x20;   P1 --> P2\[busy += 1]

&#x20;   P2 --> P3\[Actualizar max\_busy si corresponde]

&#x20;   P3 --> P4\[Generar tiempo de servicio]

&#x20;   P4 --> P5\[Agendar evento departure]

&#x20;   P5 --> I



&#x20;   O -- No --> Q\[Rechazar solicitud]

&#x20;   Q --> Q1\[rejected += 1]

&#x20;   Q1 --> I



&#x20;   M -- departure --> R\[Procesar salida]

&#x20;   R --> R1\[completed += 1]

&#x20;   R1 --> R2\[busy -= 1]

&#x20;   R2 --> I



&#x20;   Z --> Z1\[blocking\_probability = rejected / arrivals]

&#x20;   Z1 --> Z2\[utilization = area\_busy / T / capacity]

&#x20;   Z2 --> Z3\[Calcular mean\_service\_time]

&#x20;   Z3 --> Z4\[Retornar resultados]

&#x20;   Z4 --> END(\[Fin])

```

