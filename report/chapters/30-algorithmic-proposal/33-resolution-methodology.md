## 3.3. Metodología de Resolución y Criterios de Poda

La resolución del problema se articula mediante una metodología secuencial estructurada en dos etapas operativas complementarias, orientada a blindar la infraestructura computacional frente a la explosión combinatoria y minimizar el consumo de recursos externos.

La primera etapa comprende la exploración topológica y poda algorítmica sobre el grafo en memoria principal. Al recibir una solicitud compuesta por el aeropuerto de origen $u$, destino $v$ y los parámetros de viaje, el sistema ejecuta de manera inmediata una consulta sobre la estructura UFDS. Si $\text{Find}(u) \neq \text{Find}(v)$, se dictamina la desconexión topológica en tiempo $O(\alpha(|V|))$, interrumpiendo el flujo sin incurrir en cómputos innecesarios.

Superada la validación de conexidad, se disparan en paralelo las estrategias algorítmicas de optimización. Dijkstra y A\* obtienen el camino óptimo geodésico y establecen la cota temporal de referencia $T^* = f_{\text{tiempo}}^*(P_{\text{Dijkstra}})$. Simultáneamente, BFS computa la ruta con el menor número de transbordos $S^* = f_{\text{escalas}}^*(P_{\text{BFS}})$. Con estos valores umbral, el algoritmo de Backtracking inicia la exploración de trayectos alternativos aplicando tres criterios formales de poda matemática:

1. **Poda por cardinalidad de transbordos:** Se descarta de forma inmediata cualquier rama cuya profundidad acumulada exceda $k - 1 > 2$, restringiendo el espacio de itinerarios a vuelos directos, con una o con dos escalas intermedias.
2. **Poda por cota temporal relativa:** Se interrumpe la expansión de un camino parcial $P_{\text{parcial}}$ si su tiempo acumulado excede el umbral de tolerancia respecto al óptimo calculado:
   $$f_{\text{tiempo}}(P_{\text{parcial}}) > 1.5 \times T^*$$
3. **Poda por desvío geométrico ortodrómico:** Se evalúa el ángulo geodésico formado entre el vector de avance hacia el nodo adyacente y el vector director hacia el destino final. Se podan aristas que impliquen retrocesos angulares superiores a $90^\circ$ o cuya distancia ortodrómica remanente supere la distancia entre origen y destino:
   $$d_H(v_{\text{actual}}, v_{\text{destino}}) > d_H(v_{\text{origen}}, v_{\text{destino}})$$
4. **Dominancia de Pareto:** En el espacio de soluciones candidatas, un itinerario $P_A$ domina a $P_B$ ($P_A \succ P_B$) si satisface:
   $$\left( f_{\text{tiempo}}(P_A) \le f_{\text{tiempo}}(P_B) \land f_{\text{escalas}}(P_A) \le f_{\text{escalas}}(P_B) \right) \land \left( F(P_A) \neq F(P_B) \right)$$
   Las soluciones dominadas son descartadas, reteniendo únicamente el conjunto eficiente de Pareto [@shovan2025parallel].

Los itinerarios supervivientes son evaluados mediante DFS para validar la aciclicidad estricta y se procesan a través de ordenamiento topológico para garantizar la coherencia cronológica en el grafo acíclico dirigido del plan de vuelo.

La segunda etapa consiste en la validación y cotización selectiva en el mercado. En lugar de interrogar a proveedores comerciales de manera abierta sobre miles de combinaciones posibles, el conjunto de rutas se reduce estrictamente a las tres mejores alternativas del grafo. Estas opciones se someten a consulta contra las interfaces de programación de vuelos para extraer tarifas reales en moneda local, duraciones efectivas y enlaces directos de reserva. Esta delimitación metodológica garantiza un rendimiento determinista de alta velocidad y sostiene la viabilidad económica del sistema.

\newpage