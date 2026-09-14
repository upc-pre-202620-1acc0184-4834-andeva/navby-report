# Capítulo II: Descripción del Conjunto de Datos

## 2.1. Origen y Características del Dataset

Para modelar la red aerocomercial global se seleccionó el repositorio de datos abiertos OpenFlights [@patokallio2017openflights] ([openflights/data](https://github.com/jpatokal/openflights/tree/master/data)). Su estructura comprende dos fuentes primarias: **airports-extended.dat**, con 12,668 instalaciones aéreas mundiales, y **routes.dat**, con 67,663 conexiones directas programadas, complementadas por catálogos auxiliares de aerolíneas (6,162), países (261) y aeronaves (246). En la Tabla \ref{tbl:diccionario-grafo-openflights} se detallan los atributos esenciales utilizados para formalizar los vértices y aristas del sistema.

\begin{table}[H]
\centering
\caption{Diccionario de Atributos Seleccionados para el Modelado del Grafo Aéreo}
\label{tbl:diccionario-grafo-openflights}
\renewcommand{\arraystretch}{1.0}
\footnotesize
\begin{tabularx}{\textwidth}{| >{\centering\arraybackslash}m{2.2cm} | >{\centering\arraybackslash}m{2.4cm} | >{\centering\arraybackslash}m{2.1cm} | X |}
\hline
\thfirst{Componente} & \thcell{Atributo} & \thcell{Tipo de Dato} & \thcell{Propósito y Rol en el Modelado} \\
\hline
\thspanfirst{4}{Atributos de Vértices (Nodos del Grafo - airports-extended.dat)} \\
\hline
Vértice & Airport ID & Entero & Identificador numérico secuencial único asignado por la fuente. \\
\hline
Vértice & Name & Texto & Denominación oficial de la terminal o aeródromo internacional. \\
\hline
Vértice & City & Texto & Ciudad metropolitana asociada para la resolución de origen y destino. \\
\hline
Vértice & Country & Texto & Nación soberana donde opera físicamente la infraestructura. \\
\hline
Vértice & IATA & Texto (3) & Código canónico alfanumérico que actúa como identificador del nodo. \\
\hline
Vértice & Latitude & Decimal & Coordenada latitudinal en el elipsoide WGS84 ($\phi_u$). \\
\hline
Vértice & Longitude & Decimal & Coordenada longitudinal en el elipsoide WGS84 ($\lambda_u$). \\
\hline
Vértice & Type & Texto & Clasificación de la instalación aérea para el filtrado comercial. \\
\hline
\thspanfirst{4}{Atributos de Aristas (Conexiones Dirigidas - routes.dat)} \\
\hline
Arista & Airline & Texto (2-3) & Identificador de la aerolínea encargada de la operación del trayecto. \\
\hline
Arista & Source airport & Texto (3) & Código IATA de la terminal emisora (nodo origen $u \in V$). \\
\hline
Arista & Destination airport & Texto (3) & Código IATA de la terminal receptora (nodo destino $v \in V$). \\
\hline
Arista & Stops & Entero & Cantidad de escalas técnicas intermedias del servicio directo. \\
\hline
Arista & Equipment & Texto & Perfiles de aeronaves habilitadas para cubrir el trayecto. \\
\hline
\end{tabularx}
\vspace{1mm}
\noindent\raggedright\small\textit{Nota.} Elaboración propia a partir de las especificaciones estructurales de OpenFlights.
\end{table}

Las coordenadas geográficas suministran la base empírica para el cálculo de distancias geodésicas mediante la formulación de Haversine, mientras que los códigos canónicos IATA permiten articular la topología del grafo con servicios externos de cotización en tiempo real, transformando la red estática en una solución accionable para la optimización de itinerarios.