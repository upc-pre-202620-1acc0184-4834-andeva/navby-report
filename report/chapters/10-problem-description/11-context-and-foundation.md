# Capítulo I: Descripción del Problema

## 1.1. Antecedentes y Problemática

La aviación comercial transporta más de 4,700 millones de pasajeros al año con una ocupación promedio superior al 83.5% [@icao2024world; @iata2025outlook]. Con los aeropuertos centrales operando cerca de su capacidad, un retraso pequeño se propaga con facilidad a otros vuelos [@eurocontrol2025report; @li2024delay]. Las escalas concentran buena parte de este riesgo: alrededor del 40% de los incidentes de equipaje ocurren durante las transferencias entre vuelos [@sita2025baggage; @sita2026insights].

Al buscar un vuelo, el viajero debe elegir entre extremos. Ordenar por precio suele devolver itinerarios con escalas largas, y ordenar por duración suele devolver tarifas muy altas. Además, muchos buscadores priorizan aerolíneas de una misma alianza y omiten combinaciones entre aerolíneas independientes que podrían ser más convenientes [@arrieta2026hyper]. El resultado es que el usuario termina comparando decenas de opciones a mano, sin una forma objetiva de saber cuál ofrece el mejor equilibrio.

En síntesis, **el problema** es que encontrar un vuelo que equilibre precio, duración y número de escalas exige al viajero un análisis manual que las herramientas actuales no resuelven. **La mejor solución** es un sistema que evalúe esos tres criterios al mismo tiempo y entregue directamente las tres opciones con mejor balance, cada una con su enlace de compra. Navby implementa esta solución en dos pasos: primero descarta sobre un grafo de aeropuertos las rutas imposibles sin costo, y luego ordena las ofertas reales del mercado con un puntaje único que combina los tres criterios [@koelker2024analyzing; @wei2024multiobjective].
