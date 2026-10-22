# Capítulo IV: Diseño del Aplicativo

## 4.1. Arquitectura del Sistema y Procesos de Software

La arquitectura de Navby adopta un diseño desacoplado estructurado en dos componentes principales: una interfaz interactiva de usuario y una plataforma de servicios de backend implementada como un monolito modular en Python. Esta separación garantiza que el motor algorítmico y las estructuras de grafos en memoria permanezcan aislados del ciclo de renderizado web y de las operaciones de persistencia relacional.

En la @tbl:componentes-arquitectura se detallan los módulos de software que componen la plataforma, sus tecnologías base y sus responsabilidades funcionales.

| Componente | Nivel | Tecnología | Responsabilidad Principal |
| :---: | :---: | :---: | :--- |
| Cliente Web | Presentación | React 19, TypeScript, MapLibre GL | Captura de parámetros de viaje, proyección cartográfica ortodrómica y presentación interactiva del podio de ofertas. |
| Plataforma API | Servicios | Python 3.12+, FastAPI, Uvicorn | Coordinación asíncrona de solicitudes, exposición de interfaces RESTful y mediación entre módulos. |
| Motor de Rutas | Núcleo Algorítmico | Python nativo en memoria | Mantenimiento del grafo de adyacencia de 3,354 aeropuertos, ejecución de BFS para poda de escalas y trazado óptimo mediante A\*. |
| Motor de Cotización | Núcleo Algorítmico | Python, NumPy | Normalización min-max, filtrado de frontera de Pareto y cálculo de puntaje multicriterio para el podio de ofertas. |
| Caché Efímera | Infraestructura | Redis 7 | Almacenamiento temporal de cotizaciones de vuelos con tiempo de expiración de 30 minutos y control de sesiones. |
| Persistencia | Infraestructura | PostgreSQL 16 | Almacenamiento transaccional de cuentas de usuario, historial de itinerarios guardados y eventos de integración. |

: Componentes Principales de la Arquitectura de Software {#tbl:componentes-arquitectura}

*Nota.* Componentes y tecnologías que conforman la arquitectura desacoplada de Navby.

El ciclo de procesamiento de una búsqueda de vuelos se divide en dos fases concurrentes diseñadas para optimizar el tiempo de respuesta y evitar consultas externas innecesarias. Cuando el usuario especifica las ciudades de origen y destino, la aplicación cliente despacha dos solicitudes simultáneas.

La primera solicitud invoca al servicio de vista previa de rutas. El motor de rutas evalúa la conectividad sobre el grafo aeroportuario cargado en memoria mediante una búsqueda en anchura acotada a dos escalas. Si el destino no es alcanzable dentro de este límite, el proceso concluye inmediatamente informando la inviabilidad del trayecto. Si la ruta existe, se ejecuta de inmediato el algoritmo A\* para obtener el camino de mínima duración estimada ($T_{\min}$) y la secuencia de coordenadas geográficas de los aeropuertos intermedios, proyectando la trayectoria preliminar sobre el mapa en milisegundos.

La segunda solicitud gestiona la cotización y optimización multicriterio. El backend identifica todos los pares de aeropuertos posibles asociados a las áreas metropolitanas seleccionadas y ejecuta una evaluación previa con BFS y A\* para descartar combinaciones desconectadas o excesivamente largas, seleccionando únicamente los dos mejores pares comerciales. Para estos pares, el sistema verifica la existencia de tarifas vigentes en la caché de Redis; ante fallos de caché, consulta al proveedor externo de vuelos. Con las ofertas obtenidas, el motor multicriterio filtra las soluciones dominadas de Pareto, normaliza los criterios de precio, duración y escalas, y retorna las tres mejores alternativas ordenadas por su puntaje de equilibrio.
