## 4.3. Diseño Detallado del Motor Algorítmico

El motor algorítmico de Navby coordina tres técnicas especializadas en una secuencia estricta de filtros. Esta canalización asegura que las consultas externas a proveedores de tarifas se ejecuten únicamente cuando se ha demostrado analíticamente la existencia de rutas comerciales viables.

### 4.3.1. Búsqueda en Anchura para Verificación de Conectividad (BFS)

El servicio **BreadthFirstSearch** comprueba si existe al menos una ruta aérea entre el origen y el destino con un máximo de dos escalas (tres tramos de vuelo). La búsqueda inicializa una cola FIFO con el nodo de origen en nivel 0 y un conjunto de vértices visitados para evitar ciclos.

El algoritmo expande los nodos nivel por nivel. Si el aeropuerto de destino se extrae de la cola en una profundidad menor o igual a 3, la búsqueda concluye inmediatamente retornando el indicador de alcanzabilidad y el número mínimo de escalas requeridas. Si la cola se vacía o todos los caminos activos alcanzan la profundidad 3 sin localizar el destino, el par se marca como inviable y el proceso se detiene con costo cero.

### 4.3.2. Búsqueda Heurística Espacial (A\*)

Una vez confirmada la conectividad del par, el servicio **AStarSearch** calcula la ruta físicamente más rápida y su duración mínima estimada ($T_{\min}$). El espacio de estados se modela mediante el par $(u, k)$, donde $u$ es el aeropuerto actual y $k$ es la cantidad de tramos acumulados ($1 \le k \le 3$).

La exploración utiliza una cola de prioridad min-heap gobernada por la función de evaluación $f(u) = g(u) + h(u)$. La función de costo acumulado $g(u)$ suma la duración de vuelo de cada tramo según $w_t(u, v)$ e incorpora una penalización fija de 60 minutos por cada escala intermedia:

$$g(v) = g(u) + w_t(u, v) + 60 \cdot \mathbb{I}(u \neq \text{origen})$$

La heurística admisible $h(u) = \frac{d_H(u, \text{destino})}{800} \cdot 60$ estima el tiempo restante a partir de la distancia ortodrómica de círculo máximo. Dado que ningún vuelo comercial supera la velocidad de crucero en una trayectoria menor a la geodésica, $h(u)$ nunca sobreestima el costo real, garantizando la optimalidad de la ruta encontrada.

### 4.3.3. Selección de Pares de Aeropuertos en Ciudades Múltiples

Cuando una búsqueda involucra áreas metropolitanas con varios aeropuertos, el componente **PairSelector** evalúa todas las combinaciones posibles de pares origen–destino (hasta 25 combinaciones para ciudades de hasta 5 terminales). Cada combinación se somete a BFS para descartar pares inconexos y posteriormente a A\*.

Los pares alcanzables se ordenan de acuerdo a cuatro criterios jerárquicos: menor número de escalas mínimas, mayor suma de grado de salida comercial $(k_{\text{salida}}(u) + k_{\text{salida}}(v))$, menor duración física $T_{\min}$ y orden léxico. El sistema selecciona como máximo los dos pares más prometedores para su cotización en el mercado real, evitando llamadas innecesarias a aeropuertos secundarios con escasa oferta.

### 4.3.4. Motor Multicriterio y Selección del Podio

Al recibir las cotizaciones del mercado, el motor de optimización aplica un proceso de decisión multiobjetivo en dos etapas:

1. **Filtrado de Dominancia de Pareto:** El servicio **ParetoFilter** compara todas las ofertas recibidas por pares. Una oferta $a$ domina a $b$ si su precio, duración y escalas son menores o iguales a los de $b$, y estrictamente menores en al menos un criterio. Todas las soluciones dominadas se eliminan, conservando únicamente la frontera de Pareto.
2. **Puntaje Ponderado y Diversidad del Podio:** El evaluador **MulticriteriaRanker** normaliza los tres criterios entre 0 y 1 respecto a los valores extremos observados en la frontera de Pareto. Cada oferta recibe un puntaje $S \in [0, 1]$ mediante la distancia euclidiana ponderada al punto ideal:

$$S_i = \sqrt{\alpha\, p_i'^2 + \beta\, t_i'^2 + \gamma\, e_i'^2}$$

Las ofertas se ordenan de menor a mayor valor de $S$. El sistema selecciona las tres primeras opciones garantizando que no compartan la misma secuencia de aeropuertos de conexión, conformando el podio final de recomendaciones que se presenta al usuario junto a su porcentaje de afinidad $(1 - S) \times 100\%$.
