## 5.2. Evaluación Experimental y Análisis de Complejidad

El desempeño del motor algorítmico se evaluó experimentalmente mediante un script offline en Python ejecutado sobre el grafo consolidado de OpenFlights (3,354 nodos y 37,326 aristas dirigidas únicas). Para cada caso de prueba se realizaron 100 iteraciones consecutivas registrando la media y la desviación estándar del tiempo de procesamiento con el temporizador de alta resolución de la biblioteca estándar de Python.

En la Tabla \ref{tbl:benchmark-tiempos-ejecucion} se presentan las métricas de tiempo de ejecución, escalas mínimas, duración física estimada ($T_{\min}$) y estados expandidos sobre el grafo, organizadas en formato de doble fila por caso para contrastar la ruta física con su costo de exploración.

\begin{table}[htpb]
\centering
\caption{Tiempos de Ejecución y Métricas Experimentales de Enrutamiento}
\label{tbl:benchmark-tiempos-ejecucion}
\renewcommand{\arraystretch}{1.25}
\footnotesize
\begin{tabularx}{\textwidth}{| >{\centering\arraybackslash}m{3.4cm} | >{\centering\arraybackslash}m{1.8cm} | >{\centering\arraybackslash}m{2.4cm} | >{\centering\arraybackslash}m{2.4cm} | X |}
\hline
\thspanfirst{2}{Escenario de Prueba} & \thspan{2}{Tiempo de Cómputo (ms)} & \thcell{Resultado Físico y Exploración en Grafo} \\
\hline
\thfirst{Caso y Par Evaluado} & \thcell{Escalas} & \thcell{BFS} & \thcell{A*} & \thcell{Ruta Óptima ($T_{\min}$) / Nodos Expandidos} \\
\hline
\multirow{2}{3.4cm}{\centering Caso 1: Troncal\newline\textbf{LIM $\rightarrow$ SCL}}
& \multirow{2}{*}{0} & \multirow{2}{*}{0.28 $\pm$ 0.05} & \multirow{2}{*}{0.06 $\pm$ 0.03} & Ruta: LIM $\rightarrow$ SCL ($T_{\min} = 214.6$ min) \\
\cline{5-5}
& & & & Nodos expandidos: 2 estados ($< 0.1\%$ del grafo) \\
\hline
\multirow{2}{3.4cm}{\centering Caso 2: Continental\newline\textbf{LIM $\rightarrow$ EZE}}
& \multirow{2}{*}{0} & \multirow{2}{*}{0.16 $\pm$ 0.03} & \multirow{2}{*}{0.06 $\pm$ 0.04} & Ruta: LIM $\rightarrow$ EZE ($T_{\min} = 266.5$ min) \\
\cline{5-5}
& & & & Nodos expandidos: 2 estados ($< 0.1\%$ del grafo) \\
\hline
\multirow{2}{3.4cm}{\centering Caso 3: Intercont.\newline\textbf{LIM $\rightarrow$ NRT}}
& \multirow{2}{*}{1} & \multirow{2}{*}{1.20 $\pm$ 0.19} & \multirow{2}{*}{1.90 $\pm$ 0.26} & Ruta: LIM $\rightarrow$ LAX $\rightarrow$ NRT ($T_{\min} = 1280.6$ min) \\
\cline{5-5}
& & & & Nodos expandidos: 36 estados ($1.07\%$ del grafo) \\
\hline
\multirow{2}{3.4cm}{\centering Caso 4: Metropol.\newline\textbf{LHR $\rightarrow$ JFK}}
& \multirow{2}{*}{0} & \multirow{2}{*}{0.70 $\pm$ 0.08} & \multirow{2}{*}{0.19 $\pm$ 0.04} & Ruta: LHR $\rightarrow$ JFK ($T_{\min} = 445.5$ min) \\
\cline{5-5}
& & & & Nodos expandidos: 2 estados ($< 0.1\%$ del grafo) \\
\hline
\multirow{2}{3.4cm}{\centering Caso 5: Inviable\newline\textbf{AYP $\rightarrow$ AAT}}
& \multirow{2}{*}{Inviable} & \multirow{2}{*}{0.51 $\pm$ 0.40} & \multirow{2}{*}{5.38 $\pm$ 1.92} & Ruta: Inalcanzable dentro de la cota de 2 escalas \\
\cline{5-5}
& & & & Nodos: 884 visitados en BFS vs 2,926 en A* sin poda \\
\hline
\end{tabularx}
\end{table}

*Nota.* Promedio y desviación estándar calculados sobre 100 ejecuciones por caso de prueba en entorno local con Python 3.12+.

Los resultados evidencian la complementariedad de la arquitectura algorítmica:

**Eficiencia de la poda por niveles en BFS.** En todos los escenarios alcanzables, BFS determinó la existencia de ruta en menos de 1.25 ms. En el Caso 5, el algoritmo recorrió la vecindad de profundidad 3 (884 vértices) y concluyó la inviabilidad del trayecto en 0.51 ms, deteniendo el flujo con costo cero antes de invocar servicios externos.

**Poder directriz de la heurística en A\*.** En rutas directas (Casos 1, 2 y 4), la heurística Haversine guió a A\* a expandir únicamente 2 vértices (origen y destino) en menos de 0.20 ms. En el trayecto transpacífico (Caso 3), el algoritmo expandió solo 36 estados para encontrar la conexión óptima vía Los Ángeles (`LAX`), lo que representa el 1.07% de los vértices del grafo. Sin la poda previa de BFS en pares inviables (Caso 5), A\* exploraría 2,926 estados (5.38 ms).

Para evaluar la escalabilidad del motor multicriterio de Pareto de forma aislada a la latencia de red y sin consumir cuotas de proveedores externos, el script incorpora un generador estocástico con semilla fija (`seed = 42`) que sintetiza conjuntos de $N$ ofertas comerciales con correlaciones realistas de mercado entre precio, duración y escalas. Dado que la complejidad $O(N^2)$ depende exclusivamente de la cardinalidad $N$ de vectores tridimensionales en memoria, este enfoque permite medir con exactitud el tiempo neto de CPU hasta $N = 500$. En la Tabla \ref{tbl:escalabilidad-pareto} se resumen las mediciones obtenidas.

\begin{table}[htpb]
\centering
\caption{Escalabilidad Temporal del Motor Multicriterio de Pareto}
\label{tbl:escalabilidad-pareto}
\renewcommand{\arraystretch}{1.25}
\footnotesize
\begin{tabularx}{\textwidth}{| >{\centering\arraybackslash}X | >{\centering\arraybackslash}X | >{\centering\arraybackslash}X | >{\centering\arraybackslash}X |}
\hline
\thfirst{Volumen de Entrada} & \thspan{2}{Desempeño Temporal en RAM} & \thcell{Reducción de Espacio} \\
\hline
\thfirst{Ofertas Evaluadas ($N$)} & \thcell{Tiempo Promedio (ms)} & \thcell{Desviación Estándar (ms)} & \thcell{Frontera de Pareto Promedio} \\
\hline
10 & 0.009 & 0.002 & 3.3 ofertas \\
\hline
25 & 0.025 & 0.006 & 4.8 ofertas \\
\hline
50 & 0.057 & 0.011 & 5.9 ofertas \\
\hline
100 & 0.194 & 0.370 & 7.3 ofertas \\
\hline
200 & 0.368 & 0.271 & 7.8 ofertas \\
\hline
500 & 1.247 & 0.658 & 8.5 ofertas \\
\hline
\end{tabularx}
\end{table}

*Nota.* Mediciones sobre 100 evaluaciones independientes con generador sintético determinista para cada tamaño muestral $N$.

Los datos confirman el crecimiento temporal cuadrático $O(N^2)$ de la comparación por pares. Para un volumen comercial estándar de 50 a 100 ofertas por búsqueda, el filtrado de dominancia y el cálculo del podio Top 3 toman menos de 0.20 ms en RAM, y apenas 1.25 ms bajo una carga extrema de 500 ofertas. En la @fig:evidencia-terminal-benchmark se muestra la salida de ejecución del script de benchmarking en consola con el consolidado de las pruebas.

![Ejecución en Terminal del Script de Benchmarking Experimental](report/assets/graphs/benchmark-terminal-output.png){#fig:evidencia-terminal-benchmark width=95%}

*Nota.* Evidencia de ejecución en consola del script de benchmarking sobre 100 iteraciones por caso y prueba de escalabilidad de Pareto.

\newpage
