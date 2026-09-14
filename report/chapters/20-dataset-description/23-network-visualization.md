## 2.3. Visualización del Grafo Aéreo

La representación visual de la topología aerocomercial permite contrastar la distribución espacial de las conexiones y validar empíricamente los fenómenos de escala postulados en el modelado formal. En la @fig:red-global-vuelos se presenta la proyección geodésica del grafo global consolidado, trazando los 3,354 vértices activos y sus 37,326 aristas dirigidas.

![Topología de la Red Aerocomercial Global sobre el Catálogo de OpenFlights](report/assets/graphs/global-flight-network.png){#fig:red-global-vuelos width=72%}

*Nota.* Proyección geodésica del grafo completo depurado

La panorámica global evidencia una marcada heterogeneidad espacial congruente con la distribución libre de escala de la red. Se aprecian conglomerados densamente mallados en Norteamérica, Europa Occidental y Asia Oriental, interconectados a través de corredores transoceánicos troncales sobre las cuencas del Atlántico Norte y el Pacífico. En contraposición, las regiones de Sudamérica, África y Oceanía presentan una topología marcadamente radial y arborescente, donde los vuelos comerciales convergen en centros nodales primarios antes de proyectarse a destinos intercontinentales.

Esta concentración espacial de la conectividad tiene implicancias directas en el diseño de los algoritmos de optimización. La presencia de nodos hiperconectados, tales como Frankfurt (FRA), Londres Heathrow (LHR), Atlanta (ATL) o Tokio Haneda (HND), así como centros articuladores regionales como São Paulo (GRU), Bogotá (BOG) y Lima (LIM), confirma la preponderancia de estructuras centro-periferia. Dicha configuración justifica la descomposición jerárquica del espacio de búsqueda y el uso de cotas heurísticas admisibles para podar ramas combinatorias innecesarias en trayectos de larga distancia.

\newpage