# Capítulo III: Propuesta de Solución Algorítmica

## 3.1. Objetivos y Alcance de la Propuesta

El objetivo general es recomendar los tres vuelos con mejor equilibrio entre precio, duración y número de escalas para un viaje entre dos ciudades, descartando antes las rutas inviables para no consultar tarifas innecesarias [@koelker2024analyzing].

Los objetivos específicos son:

- Verificar si existe una ruta con dos escalas como máximo y calcular el mínimo de escalas posible mediante búsqueda en anchura (BFS).
- Calcular la ruta físicamente más rápida mediante el algoritmo A\* sobre el grafo ponderado por tiempo estimado de vuelo.
- Seleccionar las tres mejores ofertas reales mediante optimización multicriterio sobre la frontera de Pareto.
- Medir experimentalmente el tiempo de ejecución y la cantidad de nodos explorados por los tres algoritmos.

La solución cubre viajes de solo ida y de ida y vuelta, buscados por ciudad o por aeropuerto, con un máximo de dos escalas por trayecto. Quedan fuera del alcance los viajes con varios destinos, la venta de pasajes y el seguimiento de aeronaves en tiempo real.
