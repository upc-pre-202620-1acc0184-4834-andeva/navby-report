## 3.2. Técnicas Algorítmicas Seleccionadas

Para responder a las restricciones computacionales derivadas de la topología libre de escala y satisfacer las funciones objetivo planteadas, se seleccionó un conjunto sinérgico de técnicas algorítmicas clasificadas según su función operativa en el sistema.

En el motor de cómputo en tiempo real, la búsqueda en anchura (BFS) se implementa sobre la representación no ponderada del grafo para determinar la ruta con el menor número de aristas transitadas. Dado que cada arista representa un vuelo directo sin escalas intermedias, BFS garantiza la optimalidad en la dimensión $f_{\text{escalas}}(P)$ con una complejidad asintótica de $O(|V| + |E|)$ en tiempo y $O(|V|)$ en espacio, atendiendo a pasajeros con alta aversión hacia los transbordos [@meire2022time].

Para optimizar la dimensión temporal $f_{\text{tiempo}}(P)$, se despliega el algoritmo de Dijkstra sobre el grafo ponderado mediante la función de costo $w_t(u, v) \ge 0$. Empleando una cola de prioridad indexada (*min-heap*), el algoritmo extrae de forma determinista el itinerario de menor tiempo acumulado en $O((|V| + |E|) \log |V|)$. Sin embargo, en centros de conexión globales con factores de ramificación elevados ($k > 200$), Dijkstra expande un volumen considerable de nodos en direcciones opuestas al destino.

Para mitigar esta dispersión, se implementa el algoritmo A\*, incorporando la función de evaluación $f(u) = g(u) + h(u)$. Al formular $h(u) = d_H(u, v_{\text{destino}}) / v_{\text{crucero}}$, la cota inferior satisface la propiedad de admisibilidad ($h(u) \le d^*(u)$) y la restricción de consistencia triangular ($h(u) \le w_t(u, v) + h(v)$). Esta formulación orienta espacialmente la exploración, acotando la complejidad temporal efectiva a $O(|E| \log |V|)$ y expandiendo una fracción sustancialmente menor del grafo.

Dado que los usuarios requieren evaluar diversas opciones intermedias, se estructura un algoritmo de Backtracking con poda heurística para enumerar alternativas viables. La explosión combinatoria $O(\bar{b}^d)$ se neutraliza mediante tres restricciones: profundidad máxima de tres tramos ($d \le 3$, equivalente a $k - 1 \le 2$ escalas), cota superior de duración condicionada al tiempo óptimo ($f_{\text{tiempo}}(P) \le 1.5 \times f_{\text{tiempo}}^*(P_{\text{Dijkstra}})$) y descarte de ramas con desvíos ortodrómicos que induzcan alejamiento angular respecto al destino.

La optimización simultánea de ambas dimensiones se formaliza mediante Programación Dinámica en grafos. Definiendo el estado $(u, s)$ como el costo mínimo para alcanzar el destino desde el vértice $u$ disponiendo de $s$ escalas remanentes ($s \in \{0, 1, 2\}$), se establece la relación de recurrencia:

$$C(u, s) = \min_{v \in \text{Adj}(u)} \left\{ w_t(u, v) + t_{\text{conexión}} + C(v, s - 1) \right\}$$

con el caso base $C(v_{\text{destino}}, s) = 0$ y $C(u, 0) = w_t(u, v_{\text{destino}})$ si $(u, v_{\text{destino}}) \in E$. La memoización sobre este espacio acotado de estados permite derivar la frontera de Pareto en $O(K \cdot (|V| + |E|))$ [@shovan2025parallel].

Como técnicas de soporte estructural, se integra la estructura de datos para conjuntos disjuntos (UFDS) para verificar la conexidad entre origen y destino en tiempo casi constante $O(\alpha(|V|))$ antes de iniciar la búsqueda. Asimismo, se emplea la búsqueda en profundidad (DFS) para certificar la aciclicidad estricta ($u \neq v$) y ordenamiento topológico sobre el grafo acíclico dirigido del itinerario para validar la viabilidad cronológica de las etapas de vuelo. La @tbl:tecnicas-algoritmicas-propuesta resume las características computacionales de las técnicas seleccionadas.

| Técnica Algorítmica | Criterio de Optimización / Propósito | Complejidad Temporal | Complejidad Espacial | Rol en el Sistema |
| :------------------ | :---------------------------------- | :------------------: | :------------------: | :---------------- |
| BFS | Mínimo número de escalas ($k - 1$) | $O(|V| + |E|)$ | $O(|V|)$ | Motor en tiempo real |
| Dijkstra | Menor tiempo acumulado ($w_t \ge 0$) | $O((|V| + |E|) \log |V|)$ | $O(|V|)$ | Motor en tiempo real |
| A\* | Menor tiempo con convergencia guiada | $O(|E| \log |V|)$ | $O(|V|)$ | Motor en tiempo real |
| Backtracking con poda | Enumeración de rutas alternativas viables | $O(b_{\text{efectivo}}^d)$ | $O(d)$ | Motor en tiempo real |
| Programación Dinámica | Frontera de Pareto (tiempo vs. escalas) | $O(K \cdot (|V| + |E|))$ | $O(K \cdot |V|)$ | Motor en tiempo real |
| UFDS | Verificación instantánea de conexidad | $O(\alpha(|V|))$ | $O(|V|)$ | Validación previa |
| DFS y Ordenamiento Topológico | Garantía de aciclicidad y secuencia temporal | $O(|V| + |E|)$ | $O(|V|)$ | Validación de itinerario |

: Catálogo de Técnicas Algorítmicas Seleccionadas para la Solución {#tbl:tecnicas-algoritmicas-propuesta}

*Nota.* $|V| = 3,354$, $|E| = 37,326$, $K \le 2$ escalas máximas, $d \le 3$ profundidad y $\alpha$ denota la inversa de la función de Ackermann.
