# Capítulo V: Validación de Resultados y Pruebas

## 5.1. Casos de Prueba y Contratos de Entrada y Salida

Para evaluar el comportamiento del sistema en escenarios operacionales representativos, se diseñaron cinco casos de prueba sobre la red aerocomercial global de OpenFlights. Estos casos abarcan diferentes topologías de red: rutas troncales directas, conexiones continentales, itinerarios intercontinentales multiescala, áreas metropolitanas con múltiples aeropuertos y pares inviables que superan la restricción de dos escalas.

En la Tabla \ref{tbl:casos-prueba-sistema} se especifican los escenarios seleccionados, sus pares de aeropuertos asociados y el objetivo de validación de cada prueba.

\begin{table}[htpb]
\centering
\caption{Casos de Prueba para la Validación del Sistema}
\label{tbl:casos-prueba-sistema}
\renewcommand{\arraystretch}{1.25}
\footnotesize
\begin{tabularx}{\textwidth}{| >{\centering\arraybackslash}m{1.8cm} | >{\centering\arraybackslash}m{2.4cm} | >{\centering\arraybackslash}m{2.5cm} | >{\centering\arraybackslash}m{1.8cm} | X |}
\hline
\thfirst{Caso} & \thcell{Par Evaluado} & \thcell{Topología} & \thcell{Escalas} & \thcell{Propósito de Validación} \\
\hline
Caso 1 & LIM $\rightarrow$ SCL & Troncal directa & 0 & Conexión directa de alta densidad entre capitales sudamericanas. \\
\hline
Caso 2 & LIM $\rightarrow$ EZE & Continental & 0 & Ruta internacional de media distancia con oferta directa y con escalas. \\
\hline
Caso 3 & LIM $\rightarrow$ NRT & Intercontinental & 1 & Trayecto transpacífico de larga distancia que exige hubs de transferencia. \\
\hline
Caso 4 & LHR $\rightarrow$ JFK & Metropolitano & 0 & Corredor transatlántico con múltiples terminales en origen y destino. \\
\hline
Caso 5 & AYP $\rightarrow$ AAT & Desconectado & Inviable & Par regional aislado que no admite rutas con dos escalas o menos. \\
\hline
\end{tabularx}
\end{table}

*Nota.* Escenarios topológicos seleccionados para verificar la corrección funcional y el filtrado del motor algorítmico.

Los contratos de entrada y salida formalizan el intercambio de datos con el motor algorítmico. La entrada recibe el origen, destino, fechas, pasajeros, clase de cabina y los pesos de preferencia ($\alpha, \beta, \gamma$). La salida entrega la duración física mínima de referencia ($T_{\min}$) calculada por A\* y el podio con las tres mejores ofertas no dominadas, incluyendo precio consolidado, duración real, escalas, diferencia respecto a $T_{\min}$, enlace directo de compra y porcentaje de afinidad $(1 - S) \times 100\%$.

En la @fig:validacion-io-terminal se presenta la ejecución en terminal del script de validación funcional, evidenciando la resolución completa del Caso 3 (`LIM` $\rightarrow$ `NRT`) hasta la obtención del podio Top 3 y la detención temprana de costo cero en el Caso 5 (`AYP` $\rightarrow$ `AAT`).

![Ejecución en Terminal de la Validación de Entradas y Salidas](report/assets/graphs/io-validation-terminal.png){#fig:validacion-io-terminal width=95%}

*Nota.* Captura de salida en terminal del script de validación ejecutado con Python 3.12 y uv sobre el grafo de OpenFlights.
