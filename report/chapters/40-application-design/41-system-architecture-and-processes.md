# Capítulo IV: Diseño del Aplicativo

## 4.1. Arquitectura del Sistema y Procesos de Software

La arquitectura de Navby adopta un diseño desacoplado estructurado en una aplicación cliente interactiva y una plataforma de backend implementada como un monolito modular en Python. Esta división aísla la algoritmia sobre grafos en memoria RAM del ciclo de renderizado web y de la persistencia durable. Como se ilustra en la @fig:diagrama-contenedores, el sistema se organiza en contenedores especializados con responsabilidades delimitadas.

![Diagrama de Contenedores de la Plataforma Navby](report/assets/c4-diagrams/containers.png){#fig:diagrama-contenedores width=85%}

*Nota.* Diagrama de nivel 2 del modelo C4 que representa los contenedores y límites de la plataforma Navby.

En la @tbl:componentes-arquitectura se detallan las tecnologías y responsabilidades operativas de cada contenedor del sistema.

| Contenedor | Nivel | Tecnología | Responsabilidad Principal |
| :---: | :---: | :---: | :--- |
| Aplicación Web | Presentación | React 19, MapLibre GL | Captura de criterios de viaje, trazado de arcos ortodrómicos y visualización del podio. |
| Plataforma Backend API | Servicios | Python 3.12+, FastAPI | Exposición de servicios RESTful, mediación de solicitudes y control de flujos. |
| Motor de Rutas (RAM) | Algorítmico | Python en memoria | Mantenimiento del grafo aeroportuario, poda de escalas por BFS y cálculo de $T_{\min}$ con A\*. |
| Motor de Cotización y Podio | Algorítmico | Python, NumPy | Filtrado de soluciones dominadas de Pareto y ordenamiento multicriterio del podio Top 3. |
| Caché Efímera y Sesiones | Infraestructura | Redis 7 | Almacenamiento temporal de cotizaciones de vuelos (TTL 30 min) y control de sesiones. |
| Base de Datos Relacional | Infraestructura | PostgreSQL 16 | Persistencia de cuentas de usuario, billeteras de créditos e itinerarios guardados. |

: Componentes Principales de la Arquitectura de Software {#tbl:componentes-arquitectura}

*Nota.* Contenedores principales y responsabilidades funcionales de la arquitectura de Navby.

El procesamiento de una búsqueda opera en dos fases concurrentes para optimizar la latencia y evitar consumos externos innecesarios. En la primera fase, el sistema evalúa la conectividad en el grafo mediante BFS acotado a dos escalas y traza de forma preliminar la ruta física óptima con A\* ($T_{\min}$). En la segunda fase, se seleccionan los dos pares de aeropuertos comerciales más prometedores, se recuperan las tarifas de la caché en Redis o del proveedor externo, y se genera el podio mediante el filtro de Pareto y la ponderación multicriterio. El flujo de interacción entre los componentes se detalla en la @fig:diagrama-secuencia.

![Diagrama de Secuencia del Proceso de Consulta y Optimización](report/assets/c4-diagrams/search-sequence.png){#fig:diagrama-secuencia width=90%}

*Nota.* Secuencia de interacción y orquestación entre componentes durante la consulta y optimización de vuelos.
