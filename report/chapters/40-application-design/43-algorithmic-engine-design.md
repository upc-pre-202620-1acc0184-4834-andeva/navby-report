## 4.3. Diseño Detallado del Motor Algorítmico

El motor algorítmico de Navby coordina tres técnicas especializadas en una canalización de filtros sucesivos. Este diseño desacoplado asegura que las consultas externas a proveedores de tarifas se ejecuten únicamente cuando se ha demostrado analíticamente la existencia de rutas comerciales viables. Como se ilustra en el diagrama de actividades de la @fig:diagrama-pipeline-algoritmico, el flujo de ejecución prioriza la poda temprana de trayectos inviables con costo computacional y económico cero.

![Diagrama de Actividades del Pipeline Algorítmico](report/assets/class-diagrams/pipeline-activity-diagram.png){#fig:diagrama-pipeline-algoritmico width=75%}

*Nota.* Diagrama de actividades que modela las etapas de poda previa, búsqueda espacial guiada y optimización multiobjetivo.

En la @tbl:especificacion-algoritmos se resumen las tres técnicas integradas, detallando su rol operativo en el pipeline, condiciones de evaluación y cotas de complejidad asintótica en tiempo y memoria.

| Fase | Algoritmo | Propósito Operativo | Heurística o Criterio de Parada | Complejidad Temporal | Complejidad Espacial |
| :---: | :---: | :--- | :--- | :---: | :---: |
| Poda Previa | BFS | Comprobar conectividad y calcular escalas mínimas. | Extracción de destino o profundidad mayor a 3 tramos. | $O(V + E)$ | $O(V)$ |
| Ruta Rápida | A\* | Calcular el mínimo físico $T_{\min}$ y la ruta cartográfica preliminar. | Extracción de destino en min-heap con máximo 3 tramos. | $O(K \cdot E \log(K \cdot V))$ | $O(K \cdot V)$ |
| Podio Top 3 | Multicriterio | Filtrar ofertas no dominadas y calcular ranking de afinidad. | Evaluación por pares en Pareto y ordenamiento de podio. | $O(N^2)$ | $O(N)$ |

: Especificación y Complejidad Asintótica del Motor Algorítmico {#tbl:especificacion-algoritmos}

*Nota.* Análisis formal de complejidad asintótica de las técnicas del motor de enrutamiento y optimización.

**Búsqueda en anchura para verificación de conectividad (BFS).** El servicio recorre el grafo aeroportuario por niveles mediante una cola FIFO desde el aeropuerto de origen. La exploración se limita a una profundidad máxima de 3 tramos (equivalente a dos escalas). Si el destino no es alcanzado dentro de esta cota, el par aeroportuario se descarta inmediatamente, finalizando la búsqueda sin invocar servicios externos ni consumir créditos. Si el destino es localizado, el nivel de extracción determina el número mínimo de escalas comerciales necesarias.

**Búsqueda heurística espacial (A\*).** Con la conectividad confirmada, el algoritmo calcula el camino físicamente más rápido y su duración mínima estimada ($T_{\min}$). El espacio de estados se representa mediante la tupla $(u, k)$, donde $u$ es el vértice actual y $k$ es el contador de tramos acumulados ($1 \le k \le 3$). La función de evaluación $f(u) = g(u) + h(u)$ acumula en $g(v)$ el tiempo de vuelo estimado por Haversine más una penalización constante de 60 minutos por escala intermedia:

$$g(v) = g(u) + w_t(u, v) + 60 \cdot \mathbb{I}(u \neq \text{origen})$$

La heurística admisible y consistente $h(u) = \frac{d_H(u, \text{destino})}{800} \cdot 60$ mide el tiempo restante a partir de la distancia ortodrómica de círculo máximo en minutos. Al no existir trayectoria comercial con menor distancia que la geodésica ni mayor velocidad que la de crucero, $h(u)$ nunca sobreestima el costo real restante, asegurando la optimalidad del resultado.

**Optimización multicriterio sobre la frontera de Pareto.** Una vez obtenidas las tarifas de mercado, el motor aplica una poda de dominancia por pares sobre las $N$ ofertas recibidas. Una solución $a$ domina a $b$ si es menor o igual en precio, duración y escalas, y estrictamente menor en al menos una dimensión. Las ofertas dominadas se eliminan y las restantes se normalizan entre 0 y 1 respecto a los extremos de la frontera. Cada alternativa recibe un puntaje cuadrático $S \in [0, 1]$ respecto al punto ideal:

$$S_i = \sqrt{\alpha\, p_i'^2 + \beta\, t_i'^2 + \gamma\, e_i'^2}, \qquad \alpha + \beta + \gamma = 1$$

El sistema selecciona las tres mejores soluciones con distinta combinación de escalas y conexiones, consolidando el podio de recomendaciones presentado al usuario junto con su porcentaje de afinidad $(1 - S) \times 100\%$.
