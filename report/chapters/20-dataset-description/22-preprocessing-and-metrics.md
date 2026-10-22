## 2.2. Preprocesamiento y Topología de la Red

Los datos originales incluyen helipuertos, estaciones de tren, registros sin código IATA y rutas hacia instalaciones sin vuelos comerciales. Para obtener una red limpia se aplicaron cinco fases de depuración: las tres primeras filtran aeropuertos y las dos últimas, rutas (@tbl:fases-filtrado-openflights).

|         Fase         | Criterio de Selección              |  Registros de Entrada   |  Registros de Salida   | Propósito y Resultado en el Modelado               |
| :------------------: | :--------------------------------- | :---------------------: | :--------------------: | :------------------------------------------------- |
| Fase 1               | Tipo de instalación aérea          | 12,668 nodos            | 11,072 nodos           | Exclusión de helipuertos, puertos marítimos y estaciones ferroviarias. |
| Fase 2               | Integridad de código IATA          | 11,072 nodos            | 6,472 nodos            | Supresión de terminales sin código alfanumérico canónico de 3 letras. |
| Fase 3               | Poda de vértices aislados          | 6,472 nodos             | 3,354 nodos            | Erradicación de aeropuertos con grado de conectividad comercial nulo (*k* = 0). |
| Fase 4               | Validación de aristas activas      | 67,663 rutas            | 67,305 rutas           | Eliminación de conexiones con terminales inexistentes en el catálogo filtrado. |
| Fase 5               | Colapso de arcos paralelos         | 67,305 rutas            | 37,326 aristas         | Fusión de rutas multioperador en aristas dirigidas únicas ponderadas por tiempo. |

: Fases de Depuración y Preprocesamiento del Dataset OpenFlights {#tbl:fases-filtrado-openflights}

*Nota.* Elaboración propia mediante análisis de integridad relacional sobre los archivos crudos de OpenFlights.

Como resultado de esta depuración, se obtuvieron tres conjuntos de datos limpios en formato CSV: **airports.csv**, con los 3,354 aeropuertos comerciales activos; **routes_unique.csv**, con 37,326 rutas directas únicas y su distancia en kilómetros, a partir de la cual se calcula el tiempo estimado de vuelo; y **airlines.csv**, con 6,162 aerolíneas. En la Tabla \ref{tbl:diccionario-datasets-navby} se presenta el diccionario con los principales atributos de cada archivo.

\begingroup
\setlength{\LTleft}{0pt}
\setlength{\LTright}{\fill}
\setlength{\LTpost}{3pt}
\renewcommand{\arraystretch}{0.95}
\footnotesize
\captionsetup{indention=0pt, justification=raggedright, singlelinecheck=false}
\begin{longtable}{| >{\centering\arraybackslash}p{2.2cm} | >{\centering\arraybackslash}p{2.6cm} | >{\centering\arraybackslash}p{2.1cm} | p{7.6cm} |}
\caption{Diccionario de atributos de los datasets canónicos depurados} \label{tbl:diccionario-datasets-navby} \\
\hline
\thfirst{Componente} & \thcell{Atributo} & \thcell{Tipo de Dato} & \thcell{Propósito y Rol en el Sistema} \\
\hline
\endfirsthead

\hline
\thfirst{Componente} & \thcell{Atributo} & \thcell{Tipo de Dato} & \thcell{Propósito y Rol en el Sistema} \\
\hline
\endhead

\hline
\endfoot

\hline
\endlastfoot

\thspanfirst{4}{airports.csv (3,354 vértices del grafo)} \\
\hline
Vértice & airport\_id & Entero & Identificador numérico secuencial original de OpenFlights. \\
\hline
Vértice & name & Texto & Denominación oficial de la terminal o aeródromo comercial. \\
\hline
Vértice & city & Texto & Ciudad metropolitana servida para resolución de origen y destino. \\
\hline
Vértice & country & Texto & Nación soberana de ubicación física de la infraestructura. \\
\hline
Vértice & iata & Texto (3) & Código canónico alfanumérico que actúa como clave del nodo ($u \in V$). \\
\hline
Vértice & icao & Texto (4) & Código formal OACI de control de tráfico aéreo. \\
\hline
Vértice & latitude & Decimal & Coordenada latitudinal en el elipsoide WGS84 ($\phi_u$). \\
\hline
Vértice & longitude & Decimal & Coordenada longitudinal en el elipsoide WGS84 ($\lambda_u$). \\
\hline
Vértice & altitude & Entero & Elevación de la pista sobre el nivel medio del mar expresada en pies. \\
\hline
Vértice & timezone & Decimal & Desplazamiento horario de la terminal respecto a UTC en horas. \\
\hline
Vértice & dst & Carácter & Regla operativa de horario de verano. \\
\hline
Vértice & tz\_database\_timezone & Texto & Zona horaria canónica en formato IANA para cálculo de husos. \\
\hline
\thspanfirst{4}{routes\_unique.csv (37,326 aristas dirigidas únicas)} \\
\hline
Arista & source\_airport & Texto (3) & Código IATA de la terminal de origen del enlace ($u$). \\
\hline
Arista & destination\_airport & Texto (3) & Código IATA de la terminal de destino del enlace ($v$). \\
\hline
Arista & distance\_km & Decimal & Distancia ortodrómica de Haversine ($d_H$), base del peso en horas de vuelo. \\
\hline
Arista & operating\_airlines & Texto & Aerolíneas comerciales concurrentes que operan la conexión. \\
\hline
Arista & min\_stops & Entero & Mínima cantidad de escalas técnicas del trayecto ($0 = \text{directo}$). \\
\hline
Arista & equipment\_types & Texto & Perfiles de aeronaves habilitadas para cubrir el tramo. \\
\hline
\thspanfirst{4}{airlines.csv (6,162 aerolíneas comerciales)} \\
\hline
Operador & airline\_id & Entero & Identificador numérico secuencial único asignado por OpenFlights. \\
\hline
Operador & name & Texto & Razón social o denominación comercial de la compañía operadora. \\
\hline
Operador & alias & Texto & Nombre alternativo o alias comercial secundario. \\
\hline
Operador & iata & Texto (2) & Código canónico IATA de dos caracteres de la aerolínea comercial. \\
\hline
Operador & icao & Texto (3) & Designador de tres caracteres de control de tráfico aéreo. \\
\hline
Operador & callsign & Texto & Indicativo radiotelefónico utilizado por la tripulación de vuelo. \\
\hline
Operador & country & Texto & País de matrícula y certificación aeronáutica de la compañía. \\
\hline
Operador & active & Carácter & Indicador de actividad operacional comercial de la aerolínea. \\
\end{longtable}
\endgroup

\noindent{\small\textit{Nota.} Elaboración propia a partir de los datasets canónicos depurados.\par}

La red resultante tiene una densidad de 0.33%: la gran mayoría de pares de aeropuertos no tiene una ruta directa. Por eso el grafo se guarda en memoria como listas de adyacencia, que solo almacenan las rutas existentes y permiten consultar las conexiones de cada aeropuerto de forma inmediata.

Asimismo, la red está desbalanceada: un aeropuerto promedio suma 22 rutas entre entrantes y salientes, mientras que Frankfurt (FRA) suma 477 y París-Charles de Gaulle (CDG) 470 [@wandelt2025network]. El transporte aéreo se organiza alrededor de estos aeropuertos centrales, por lo que limitar las escalas y guiar la búsqueda hacia el destino es indispensable para encontrar rutas viables con rapidez.

