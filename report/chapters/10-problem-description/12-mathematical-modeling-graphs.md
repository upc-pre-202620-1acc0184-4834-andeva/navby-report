## 1.2. Formalización Matemática del Grafo Aéreo

La red aerocomercial se modela formalmente como un grafo dirigido y ponderado $G = (V, E, W)$. El conjunto de vértices $V$ representa las terminales aeroportuarias comerciales georreferenciadas mediante coordenadas geográficas expresadas en latitud ($\phi_u$) y longitud ($\lambda_u$) bajo el elipsoide WGS84, junto a su código canónico IATA, consolidando $|V| = 3,354$ nodos comerciales activos. El conjunto de aristas dirigidas $E \subseteq V \times V$ modela las rutas directas programadas entre un aeropuerto origen $u$ y un destino $v$, totalizando $|E| = 37,326$ conexiones operativas únicas.

Dado que la base topológica no incluye horarios ni frecuencias dinámicas, la distancia ortodrómica mínima entre terminales se determina mediante la formulación trigonométrica de Haversine:

$$d_H(u, v) = 2 R \arcsin \left( \sqrt{ \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_u) \cos(\phi_v) \sin^2\left(\frac{\Delta \lambda}{2}\right) } \right)$$

En esta formulación, $R \approx 6,371\text{ km}$ corresponde al radio medio terrestre, $\Delta \phi = \phi_v - \phi_u$ representa la diferencia de latitud angular entre el aeropuerto de destino $v$ y el de origen $u$, y $\Delta \lambda = \lambda_v - \lambda_u$ define la diferencia angular de longitud entre ambas terminales.

El tiempo estimado de vuelo para cada arco dirigido se deriva a partir de la distancia geodésica calculada, integrando la velocidad de crucero y los tiempos operacionales de maniobra:

$$w_t(u, v) = \frac{d_H(u, v)}{v_{\text{crucero}}} + t_{\text{maniobra}}$$

Para este cálculo se adopta una velocidad crucero promedio de 800 km/h ($v_{\text{crucero}}$) y un tiempo adicional de maniobra de 30 minutos ($t_{\text{maniobra}}$), el cual contempla las etapas de despegue, aproximación y rodaje en pista.

Para un itinerario compuesto $P = (v_0, v_1, \dots, v_k)$ que comprende $k - 1$ escalas intermedias, la evaluación de costo se modela mediante dos funciones objetivo que cuantifican la duración acumulada y la cantidad de transbordos, incorporando una penalización fija por conexión de 60 minutos ($t_{\text{conexión}}$) en cada escala intermedia:

$$\begin{aligned}
f_{\text{tiempo}}(P) &= \sum_{i=1}^{k} w_t(v_{i-1}, v_i) + \sum_{i=1}^{k-1} t_{\text{conexión}}(v_i) \\
f_{\text{escalas}}(P) &= k - 1
\end{aligned}$$

El vector resultante $F(P) = \left(f_{\text{tiempo}}(P), f_{\text{escalas}}(P)\right)$ define el espacio de soluciones sujeto a dominancia de Pareto [@shovan2025parallel], donde un itinerario se considera óptimo si no existe otra alternativa que reduzca el tiempo de viaje sin incrementar las escalas, o viceversa.

La exploración sobre esta red aérea enfrenta una severa explosión combinatoria del espacio de estados de orden $O(\bar{b}^d)$, donde el factor de ramificación medio $\bar{b} \approx 22.26$ supera las 230 conexiones en los principales centros nodales [@wandelt2025network]. Esta intratabilidad descarta el uso de fuerza bruta y fundamenta el despliegue de técnicas algorítmicas estructuradas: BFS para el aislamiento de rutas con mínimo número de escalas y Dijkstra para optimizar el tiempo total acumulado.

Para orientar la búsqueda hacia el destino mediante A*, se formula la función heurística admisible y consistente basada en la distancia ortodrómica remanente:

$$h(u) = \frac{d_H(u, v_{\text{destino}})}{v_{\text{crucero}}}$$

Esta cota inferior garantiza la convergencia al camino óptimo sin sobrestimar el costo real de vuelo, complementándose con podas heurísticas por cota temporal y desvío geométrico en Backtracking, y Programación Dinámica para computar la frontera de Pareto del viaje.

\newpage
