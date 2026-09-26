# Capítulo III: Propuesta de Solución Algorítmica

## 3.1. Objetivos y Alcance de la Propuesta

El propósito de la propuesta algorítmica radica en resolver de manera determinista, eficiente y escalable la disyuntiva multiobjetivo inherente a la planificación de itinerarios aéreos comerciales [@koelker2024analyzing], articulando la optimización topológica sobre el grafo aéreo global con la viabilidad y disponibilidad real de boletos de mercado.

Como objetivo general, se plantea diseñar e implementar un sistema de optimización de rutas sobre la red aerocomercial consolidada de OpenFlights ($|V| = 3,354$, $|E| = 37,326$), capaz de aislar los caminos de mínima duración temporal y menor cantidad de escalas intermedias en tiempos de respuesta subsegundo, prefiltrando el universo de combinaciones viables antes de efectuar cotizaciones tarifarias externas.

Para la consecución de este fin, se definen los siguientes objetivos específicos:

1. **Aislamiento de trayectos por escalas mínimas:** Implementar algoritmos de recorrido por niveles sobre el grafo no ponderado para computar los itinerarios con la menor cantidad de transbordos posibles, minimizando el riesgo operativo de transbordo reportado por la industria [@sita2025baggage].
2. **Determinación de caminos de tiempo mínimo:** Aplicar algoritmos voraces de camino más corto sobre la red ponderada con distancias de Haversine y tiempos operacionales, identificando la ruta geodésicamente óptima.
3. **Aceleración espacial mediante heurística admisible:** Orientar la exploración hacia la terminal de destino utilizando la distancia ortodrómica remanente como función heurística admisible y consistente, reduciendo la expansión de vértices en centros nodales de alta densidad.
4. **Exploración acotada de alternativas viables:** Estructurar un esquema de búsqueda exhaustiva controlada con podas heurísticas por profundidad, cota de duración y desvío angular, extrayendo una terna representativa de itinerarios disjuntos con a lo sumo dos escalas intermedias.
5. **Aproximación de la frontera de Pareto multiobjetivo:** Formular un modelo de programación dinámica que resuelva la recurrencia sobre estados acotados de escalas remanentes, identificando las soluciones no dominadas en tiempo y transbordos [@shovan2025parallel].
6. **Garantía de integridad y aciclicidad:** Asegurar la conectividad previa entre pares de terminales en tiempo casi constante y certificar la estricta aciclicidad y secuenciación cronológica de las escalas que conforman el itinerario.

El alcance de la solución se enfoca en la perspectiva del pasajero para viajes comerciales de solo ida y de ida y vuelta entre aeropuertos reconocidos por la Asociación Internacional de Transporte Aéreo. Se excluyen del perímetro analítico trayectos con múltiples destinos fijos impuestos manualmente, la reserva transaccional de asientos físicos y la telemetría satelital en tiempo real, concentrando la capacidad de cómputo en la resolución algorítmica del grafo y la selección multicriterio de las tres alternativas óptimas de viaje.
