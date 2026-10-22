## 3.3. Metodología de Resolución

Cada búsqueda se resuelve en dos etapas. La primera usa solo el grafo en memoria y no tiene costo. La segunda consulta las ofertas reales y las ordena.

### Etapa 1: exploración del grafo

**BFS.** El sistema recorre el grafo por niveles desde el aeropuerto de origen: primero los destinos directos, luego los alcanzables con una escala y finalmente con dos. Si el destino no aparece en esos tres niveles, la búsqueda termina sin consultar tarifas. Si aparece, el nivel en que se encontró indica el mínimo de escalas posible. El usuario elige ciudades y no aeropuertos. Cuando una ciudad tiene varios aeropuertos, BFS y A\* evalúan todas las combinaciones de origen y destino, y solo se cotizan las dos más prometedoras: las de menos escalas y, entre ellas, las de aeropuertos con más rutas directas y menor tiempo estimado.

**A\*.** Con la ruta confirmada, A\* calcula la ruta más rápida. El tiempo de cada tramo es el definido en la sección 1.2, y cada escala agrega 60 minutos de conexión. Así, el tiempo estimado de una ruta $P = (v_0, v_1, \ldots, v_k)$ de $k$ tramos es:

$$T(P) = \sum_{i=0}^{k-1} w_t(v_i, v_{i+1}) + (k - 1)\, t_{\text{conexión}}$$

La penalización por escala evita que la ruta óptima se fragmente en muchos tramos cortos, algo que no ocurre en la operación real. Para decidir qué aeropuerto explorar primero, A\* estima el tiempo que falta hasta el destino desde el aeropuerto evaluado:

$$h(u) = \frac{d_H(u, \text{destino})}{v_{\text{crucero}}}$$

Esta estimación nunca supera el tiempo real, porque ningún vuelo recorre menos que el arco de círculo máximo ni viaja más rápido que la velocidad de crucero. Por ello A\* encuentra siempre la ruta óptima. La búsqueda se limita a tres tramos para respetar el máximo de dos escalas. El resultado entrega dos datos: la duración mínima físicamente posible, denotada $T_{\min}$, y la secuencia de aeropuertos que el mapa dibuja mientras se obtienen las tarifas.

### Etapa 2: selección multicriterio

El sistema consulta al proveedor de tarifas, que devuelve las ofertas vigentes con su precio total, duración real y número de escalas. Sobre ellas se aplican cuatro pasos.

Primero, se eliminan las ofertas **dominadas**: aquellas para las que existe otra igual o mejor en los tres criterios y estrictamente mejor en al menos uno. Las ofertas restantes forman la frontera de Pareto.

Segundo, cada criterio se normaliza entre 0 y 1 respecto a la mejor y la peor oferta de la frontera:

$$x_i' = \frac{x_i - x_{\min}}{x_{\max} - x_{\min}}$$

El valor 0 corresponde a la mejor oferta disponible en ese criterio. Se usa la mejor oferta real y no $T_{\min}$ porque $T_{\min}$ no incluye los tiempos de espera en aeropuertos. Si se usara, ninguna oferta alcanzaría el valor 0 en duración y el precio terminaría pesando más de lo indicado.

Tercero, cada oferta recibe un puntaje igual a su distancia ponderada al punto ideal $(0, 0, 0)$:

$$S_i = \sqrt{\alpha\, p_i'^2 + \beta\, t_i'^2 + \gamma\, e_i'^2}, \qquad \alpha + \beta + \gamma = 1$$

donde $p_i'$, $t_i'$ y $e_i'$ son el precio, la duración y las escalas normalizados. Los pesos predeterminados son 0.5 para el precio, 0.3 para la duración y 0.2 para las escalas, porque el segmento de viajeros objetivo es especialmente sensible al precio. El usuario puede cambiarlos. Como la frontera de Pareto no depende de los pesos, cambiarlos solo reordena las ofertas ya obtenidas, sin una nueva consulta [@shovan2025parallel].

Cuarto, las ofertas se ordenan de menor a mayor puntaje y se eligen las tres primeras como recomendaciones, descartando las que repiten exactamente la misma secuencia de aeropuertos que una ya elegida. Así, las tres recomendaciones salen de un mismo criterio de equilibrio y no de optimizar cada criterio por separado. Cada recomendación muestra además cuánto supera a $T_{\min}$, lo que indica al usuario el tiempo extra que añaden las esperas reales.

\newpage
