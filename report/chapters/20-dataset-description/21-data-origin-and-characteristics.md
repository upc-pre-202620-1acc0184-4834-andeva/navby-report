# Capítulo II: Descripción del Conjunto de Datos

## 2.1. Origen y Características del Dataset

Para modelar la red aerocomercial global se seleccionó el repositorio de datos abiertos OpenFlights [@patokallio2017openflights] ([openflights/data](https://github.com/jpatokal/openflights/tree/master/data)), muy utilizado en estudios de transporte y redes [@wandelt2025network]. Se usan tres archivos: **airports-extended.dat**, que recopila 12,668 instalaciones aéreas mundiales, **routes.dat**, que registra 67,663 conexiones directas regulares entre terminales, y **airlines.dat**, que cataloga 6,162 compañías aéreas comerciales.

En la Tabla \ref{tbl:diccionario-datasets-openflights} se detallan los 31 atributos originales provistos por la fuente para la caracterización del sistema.

\begingroup
\setlength{\LTleft}{0pt}
\setlength{\LTright}{\fill}
\setlength{\LTpost}{3pt}
\renewcommand{\arraystretch}{0.95}
\footnotesize
\captionsetup{indention=0pt, justification=raggedright, singlelinecheck=false}
\begin{longtable}{| >{\centering\arraybackslash}p{2.2cm} | >{\centering\arraybackslash}p{2.6cm} | >{\centering\arraybackslash}p{2.1cm} | p{7.6cm} |}
\caption{Diccionario de atributos de los datasets originales de OpenFlights} \label{tbl:diccionario-datasets-openflights} \\
\hline
\thfirst{Componente} & \thcell{Atributo} & \thcell{Tipo de Dato} & \thcell{Propósito y Rol en la Fuente} \\
\hline
\endfirsthead

\hline
\thfirst{Componente} & \thcell{Atributo} & \thcell{Tipo de Dato} & \thcell{Propósito y Rol en la Fuente} \\
\hline
\endhead

\hline
\endfoot

\hline
\endlastfoot

\thspanfirst{4}{airports-extended.dat} \\
\hline
Vértice & Airport ID & Entero & Identificador numérico secuencial único asignado por OpenFlights al registro. \\
\hline
Vértice & Name & Texto & Denominación oficial de la terminal o aeródromo internacional. \\
\hline
Vértice & City & Texto & Ciudad metropolitana asociada para la resolución de origen y destino. \\
\hline
Vértice & Country & Texto & Nación soberana donde opera físicamente la infraestructura aérea. \\
\hline
Vértice & IATA & Texto (3) & Código canónico alfanumérico que actúa como identificador del nodo. \\
\hline
Vértice & ICAO & Texto (4) & Código formal de la Organización de Aviación Civil Internacional. \\
\hline
Vértice & Latitude & Decimal & Coordenada latitudinal en el elipsoide WGS84 ($\phi_u$). \\
\hline
Vértice & Longitude & Decimal & Coordenada longitudinal en el elipsoide WGS84 ($\lambda_u$). \\
\hline
Vértice & Altitude & Entero & Elevación de la pista respecto al nivel medio del mar expresada en pies. \\
\hline
Vértice & Timezone & Decimal & Desplazamiento horario de la terminal respecto a UTC en horas decimales. \\
\hline
Vértice & DST & Carácter & Regla operativa de horario de verano. \\
\hline
Vértice & Tz database time zone & Texto & Zona horaria canónica en formato IANA. \\
\hline
Vértice & Type & Texto & Clasificación de la instalación aérea para el filtrado comercial. \\
\hline
Vértice & Source & Texto & Fuente original de procedencia del registro. \\
\hline
\thspanfirst{4}{routes.dat} \\
\hline
Arista & Airline & Texto (2-3) & Identificador IATA o ICAO de la aerolínea encargada de la operación del trayecto. \\
\hline
Arista & Airline ID & Entero & Identificador numérico secuencial de OpenFlights para la aerolínea. \\
\hline
Arista & Source airport & Texto (3-4) & Código IATA o ICAO de la terminal origen. \\
\hline
Arista & Source airport ID & Entero & Identificador numérico de OpenFlights para la terminal de origen. \\
\hline
Arista & Destination airport & Texto (3-4) & Código IATA o ICAO de la terminal destino. \\
\hline
Arista & Destination airport ID & Entero & Identificador numérico de OpenFlights para la terminal de destino. \\
\hline
Arista & Codeshare & Carácter & Indicador de operación bajo código compartido. \\
\hline
Arista & Stops & Entero & Cantidad de escalas técnicas intermedias del servicio. \\
\hline
Arista & Equipment & Texto & Perfiles de aeronaves habilitadas para cubrir el trayecto regular. \\
\hline
\thspanfirst{4}{airlines.dat} \\
\hline
Operador & Airline ID & Entero & Identificador numérico secuencial único asignado a la aerolínea. \\
\hline
Operador & Name & Texto & Razón social o denominación comercial de la compañía operadora. \\
\hline
Operador & Alias & Texto & Nombre alternativo o alias comercial secundario. \\
\hline
Operador & IATA & Texto (2) & Código canónico IATA de dos caracteres de la aerolínea comercial. \\
\hline
Operador & ICAO & Texto (3) & Designador de tres caracteres de la Organización de Aviación Civil Internacional. \\
\hline
Operador & Callsign & Texto & Indicativo radiotelefónico utilizado por la tripulación en el control aéreo. \\
\hline
Operador & Country & Texto & País de matrícula y certificación aeronáutica de la compañía. \\
\hline
Operador & Active & Texto (1) & Indicador de actividad operacional comercial de la aerolínea. \\
\end{longtable}
\endgroup

\noindent{\small\textit{Nota.} Elaboración propia a partir de las especificaciones estructurales de OpenFlights.\par}

Las coordenadas permiten calcular la distancia entre aeropuertos con la fórmula de Haversine y, a partir de ella, el tiempo estimado de cada ruta. Los códigos IATA conectan el grafo con el servicio que entrega las tarifas reales. Estas tres fuentes son la entrada del proceso de depuración descrito en la siguiente sección.