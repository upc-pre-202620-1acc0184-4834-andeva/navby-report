## 2.2. Preprocesamiento y Topología de la Red

La base cruda de OpenFlights contiene registros heterogéneos e inconsistencias referenciales inadecuadas para el ruteo algorítmico directo. Para garantizar un grafo dirigido $G = (V, E)$ computacionalmente íntegro y libre de anomalías topológicas, se implementó un proceso de depuración en cuatro fases secuenciales, resumido en la @tbl:fases-filtrado-openflights.

| Fase | Criterio de Selección | Entrada | Salida | Propósito en el Modelado |
| :--------: | :------------------------ | :-----------------: | :-----------------: | :------------------------------------------------ |
| Fase 1 | Tipo de instalación aérea | 12,668 nodos | 11,072 nodos | Exclusión de helipuertos, puertos e infraestructuras terrestres. |
| Fase 2 | Integridad de código IATA | 11,072 nodos | 6,472 nodos | Eliminación de terminales con identificadores nulos o defectuosos. |
| Fase 3 | Validación de aristas activas | 67,663 rutas | 67,305 rutas | Supresión de arcos con terminales inexistentes en el catálogo filtrado. |
| Fase 4 | Poda de vértices aislados | 6,472 nodos | 3,354 nodos | Erradicación de terminales sin grado de conectividad comercial ($k = 0$). |

: Fases de Filtrado y Sanitización de los Datos de OpenFlights {#tbl:fases-filtrado-openflights}

*Nota.* Elaboración propia mediante análisis de integridad relacional sobre OpenFlights.

Al culminar la depuración, el catálogo de vuelos conforma un multigrafo de 67,305 trayectorias comerciales concurrentes, originadas por la coexistencia de múltiples aerolíneas sobre un mismo par de terminales. Para optimizar el rendimiento de los algoritmos de ruteo en memoria principal, se colapsaron los arcos paralelos en un grafo simple dirigido de $|V| = 3,354$ vértices y $|E| = 37,326$ aristas únicas ponderadas por distancia ortodrómica. La @tbl:metricas-grafo-consolidado sintetiza sus propiedades estructurales.

| Métrica Estructural | Valor Calculado | Implicancia Algorítmica y Computacional |
| :-------------------------------: | :------------------: | :------------------------------------------------ |
| Vértices activos ($|V|$) | 3,354 | Dimensión de la tabla de adyacencia e indexación por código IATA. |
| Aristas dirigidas únicas ($|E|$) | 37,326 | Conexiones directas ponderadas por distancia geodésica Haversine. |
| Rutas comerciales operativas | 67,305 | Multigrafo original con frecuencias de múltiples aerolíneas concurrentes. |
| Densidad del grafo ($D$) | 0.00332 | Red marcadamente dispersa que optimiza el empleo de listas de adyacencia. |
| Grado medio de los nodos ($\bar{k}$) | 22.26 | Factor de ramificación promedio en recorridos en anchura y profundidad. |
| Grado máximo ($k_{\max}$) | 477 (FRA) | Concentración hiperconectada en centros globales de conexión (*hubs*). |

: Métricas Topológicas del Grafo Aéreo Consolidado {#tbl:metricas-grafo-consolidado}

*Nota.* Densidad computada formalmente como $D = \frac{|E|}{|V|(|V|-1)}$.

La densidad obtenida ($D \approx 0.33\%$) confirma que la red aerocomercial es marcadamente dispersa. Esta propiedad descarta el empleo de matrices de adyacencia por su consumo cuadrático ($O(|V|^2)$), fundamentando la implementación de listas de adyacencia indexadas mediante tablas hash con costo espacial óptimo $O(|V| + |E|)$.

Asimismo, la distribución asimétrica del grado nodal, donde centros como Frankfurt (FRA, 477 conexiones) y París (CDG, 470 conexiones) superan ampliamente la media de 22.26 enlaces, ratifica la presencia de una topología libre de escala [@wandelt2025network]. Esta hiperconectividad local acelera la expansión del espacio de estados, tornando indispensable el diseño de podas heurísticas en los algoritmos de búsqueda.

