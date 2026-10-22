# Conclusiones y Trabajo Futuro

## Conclusiones

La experimentación cuantitativa desarrollada sobre la red global de OpenFlights demuestra que la integración secuencial de búsqueda en anchura (BFS), el algoritmo A\* guiado por la heurística ortodrómica de Haversine y el filtrado multiobjetivo de Pareto resuelve de forma eficiente la planificación de vuelos bajo múltiples criterios en conflicto. La búsqueda en anchura acotada a dos escalas protege al sistema de costos computacionales e integraciones externas innecesarias, descartando pares inviables en menos de 0.60 ms. Por su parte, la admisibilidad de la heurística espacial en A\* reduce la exploración a menos del 1.1% del grafo en rutas intercontinentales complejas, mientras que el motor de Pareto depura el espacio de ofertas en menos de 0.20 ms en memoria RAM. Esta arquitectura algorítmica permite entregar un podio balanceado de tres recomendaciones en tiempos imperceptibles para el usuario, superando las limitaciones de los buscadores comerciales tradicionales que obligan a optimizar dimensiones aisladas.

## Trabajo Futuro

Como líneas de investigación y desarrollo futuro para la plataforma Navby, se plantean tres extensiones principales:

- **Incorporación de modelos predictivos de puntualidad:** Integrar modelos probabilísticos entrenados con datos meteorológicos e históricos de demoras para ajustar dinámicamente la penalización de conexión según el aeropuerto y la temporada del año.
- **Soporte para itinerarios multidestino:** Extender la formulación del grafo para soportar la planificación de viajes de múltiples paradas (*open-jaw* o *round-the-world*) mediante técnicas de descomposición geográfica por regiones IATA.
- **Optimización ecológica con huella de carbono:** Añadir el volumen de emisiones de dióxido de carbono ($\text{CO}_2$) por pasajero como un cuarto criterio explícito en la frontera de Pareto, permitiendo a los usuarios priorizar itinerarios ambientalmente eficientes.

\newpage
