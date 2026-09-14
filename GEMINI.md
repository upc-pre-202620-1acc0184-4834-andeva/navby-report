# Guía de Trabajo y Reglas del Proyecto (GEMINI.md)

Este documento establece las instrucciones, convenciones arquitectónicas, estándares de ingeniería, criterios de redacción académica y flujos de trabajo que rigen el repositorio `navby-report`.

---

## 1. Descripción del Proyecto y Doble Alcance Documental

`navby-report` es el repositorio central del equipo de startup **Andeva** para el diseño del producto **Navby** (plataforma inteligente de planificación de rutas de vuelo que combina optimización sobre grafos y tarifas de mercado en tiempo real).

El repositorio gestiona dos ámbitos documentales claramente diferenciados:

### 1.1. Ámbito Académico Oficial: Reporte del Curso Complejidad Algorítmica (`report/`)
* **Asignatura:** 1ACC0184 - Complejidad Algorítmica (UPC).
* **Propósito:** Elaboración formal de la memoria de ingeniería y reporte de entregables para los hitos del curso (TB1 e informe final TB2).
* **Enfoque:** Aplicación rigurosa de teoría de grafos y algoritmos de optimización (BFS, DFS, Dijkstra, A*, Bellman-Ford, Floyd-Warshall, UFDS, MST, Programación Dinámica) sobre una red aeroportuaria modelada con datos de OpenFlights.
* **Estándar:** Formato académico estricto bajo la **7.ª edición de las Normas APA (APA 7)** mediante el paradigma **Docs as Code**.
* **Límite de alcance:** Este documento oficial **no debe sobrecargarse** con el diseño táctico DDD detallado del backend, ya que la cátedra de Complejidad Algorítmica evalúa exclusivamente el problema, dataset de grafos, propuesta algorítmica, validación de resultados y diseño general del aplicativo.

### 1.2. Ámbito de Ingeniería de Software: Documentación Extendida del Sistema (`docs/`)
* **Propósito:** Guía maestra de arquitectura e ingeniería para el ecosistema desacoplado de Navby:
  * **Backend Platform (`docs/backend-documentation/`):** Monolito modular en Python 3.12+, FastAPI, uv, PostgreSQL 16, Redis 7 y Caddy 2, gobernado por Clean Architecture, Tactical-Level DDD-lite, CQRS-lite y Transactional Outbox.
  * **Frontend Ecosistema (`docs/frontend-architecture/`):** Website público en Astro 5 SSG con GSAP 3 y Lenis; y Webapp interactiva en React 19 SPA con mapa plano 2D MapLibre GL, deck.gl, TanStack Query, Zustand, boneyard y Sileo.
  * **Datasets Canónicos (`docs/navby-datasets/`):** Pipeline depurado de OpenFlights consolidando 3,354 nodos aeroportuarios comerciales y 37,326 aristas dirigidas únicas (colapso de arcos paralelos desde un multigrafo original de 67,305 rutas comerciales concurrentes multioperador).
* **Origen metodológico:** Adopta la estructura de la rúbrica del curso **Aplicaciones Para Dispositivos Móviles** para el modelado de software empresarial de alta fidelidad.
* **Destino:** Todo este desarrollo técnico reside en la carpeta `docs/`, manteniéndose desacoplado y separado de la entrega académica de `report/`.

---

## 2. Rúbrica de Complejidad Algorítmica (1ACC0184) y Estructura de `report/`

La memoria de ingeniería en `report/` responde a las competencias del curso (Razonamiento Cuantitativo Nivel 2 y ABET 4: Responsabilidad y Ética) y al **Caso de Estudio 9: Planificación de vuelos (LATAM Airlines / Navby)**:

### 2.1. Hitos de Evaluación
1. **Primer Hito (TB1 - Semana 6):**
   * **Descripción del problema:** Fundamentación y justificación citando fuentes académicas.
   * **Descripción y visualización del dataset:** Red de aeropuertos y rutas (OpenFlights) que cumpla con el requisito mínimo de **1500 nodos** (el dataset de Navby consolida **3,354 nodos comerciales** con grado $k \ge 1$ y **37,326 aristas dirigidas únicas**, tras colapsar el multigrafo de 67,305 rutas operativas concurrentes). Visualización cartográfica de la red global de vuelos mediante arcos geodésicos ortodrómicos (Haversine).
   * **Propuesta preliminar:** Definición del objetivo de la propuesta, técnicas algorítmicas y metodología preliminar.
2. **Segundo Hito (Semana 13):**
   * Consolidación del problema, dataset y propuesta técnica definitiva.
   * **Diseño del aplicativo:** Procesos de ingeniería de software y análisis algorítmico del sistema.
3. **Tercer Hito (TB2 - Semana 14 / Exposición Semana 15):**
   * Informe final completo (entre 4 y 10 páginas según rúbrica base) incluyendo:
     * Validación de resultados y pruebas (entradas, salidas, comparación de tiempos de ejecución y complejidad asintótica).
     * Conclusiones fundamentadas en el experimento y trabajo futuro.
     * Referencias bibliográficas en formato APA 7.
   * Ensamblado con la aplicación funcional en Python (algoritmia de backend) y GUI interactiva.

### 2.2. Técnicas Algorítmicas Aceptadas por la Cátedra y Mapeo en Navby
Las técnicas de la rúbrica se estructuran operativamente en tres ámbitos de ejecución:
1. **Motor de Rutas en Tiempo Real (Runtime / Python):**
   * **BFS:** Rutas con el mínimo número de escalas posibles ($O(V + E)$).
   * **Dijkstra:** Caminos de menor tiempo estimado acumulado sobre aristas ponderadas Haversine ($O((V + E) \log V)$).
   * **A\*:** Búsqueda voraz guiada por la heurística admisible de distancia ortodrómica directa al destino ($O(E \log V)$).
   * **Backtracking con Poda:** Enumeración acotada de rutas alternativas viables con poda por escalas ($\le 2$), duración y desvío geométrico ($O(b^d)$ acotado).
   * **Programación Dinámica (DP en grafos):** Optimización multi-criterio balanceando tiempo de vuelo y escalas mediante recurrencia sobre estados $(u, \text{escalas\_restantes})$ ($O(K \cdot (V + E))$).
   * **Divide y Vencerás:** Descomposición intercontinental por macro-regiones IATA y hubs de transferencia (*gateways*).
   * **DFS:** Detección de ciclos y validación de aciclicidad en itinerarios multiconexión ($u \neq v$).
2. **Preprocesamiento, Conectividad y Estructura (Data Pipeline / Offline):**
   * **UFDS (Union-Find Disjoint Sets):** Poda de terminales aisladas ($k = 0$), validación de conectividad previa en $O(\alpha(V))$ y estructura base para Kruskal.
   * **SCC (Tarjan / Kosaraju):** Detección de la componente fuertemente conexa dominante y análisis de centralidad de hubs globales.
   * **MST (Kruskal o Prim):** Construcción del esqueleto de conectividad de distancia mínima y análisis de resiliencia/redundancia de la red.
   * **Ordenamiento Topológico:** Secuenciación temporal estricta de las etapas de vuelo en el DAG de itinerarios ($t_{\text{salida}}^{i+1} > t_{\text{llegada}}^i + t_{\text{conexión}}$).
3. **Validación y Benchmarking Asintótico (Reporte Académico):**
   * **Fuerza Bruta:** Cota inferior de optimalidad y demostración experimental de la explosión combinatoria en subgrafos pequeños ($N \le 10$).
   * **Bellman-Ford:** Demostración empírica de ineficiencia ($O(V \cdot E)$) frente a Dijkstra en grafos con pesos no negativos ($w_t \ge 0$).
   * **Floyd-Warshall:** Programación dinámica todos-a-todos ($O(V^3)$) en subgrafos densos de principales hubs.
   * **Flujo Máximo (Edmonds-Karp / Dinic):** Modelado experimental de capacidad teórica y saturación de corredores aéreos troncales.

---

## 3. Estándar de Backend y Tactical-Level DDD (`docs/backend-documentation/`)

Para la documentación extendida en `docs/`, se sigue la especificación táctica inspirada en la rúbrica de diseño de software móvil y empresarial:

### 3.1. Estructura de Capas por Bounded Context
Cada Bounded Context se documenta y estructura en cuatro capas desacopladas:
1. **Domain Layer (Capa de Dominio):**
   * Clases nucleares independientes de frameworks (Python puro).
   * **Aggregates:** Raíces de agregado derivadas de `AbstractDomainAggregateRoot`.
   * **Entities & Value Objects:** Inmutables mediante `@dataclass(frozen=True)` con validaciones estrictas en `__post_init__`.
   * **Domain Events:** Eventos inmutables que notifican cambios de estado en los agregados.
   * **Repository Interfaces:** Contratos puros de persistencia (`typing.Protocol`).
   * **Diccionario de clases:** Documentación detallada por clase con nombre, propósito, miembros (atributos, métodos, visibilidad `public`, `private`, `protected`) y relaciones.
2. **Application Layer (Capa de Aplicación):**
   * Casos de uso segregados mediante **CQRS**:
     * **Commands y Command Handlers:** Mutaciones de estado y orquestación.
     * **Queries y Query Handlers:** Consultas de lectura optimizadas.
     * **Event Handlers:** Manejadores de eventos de dominio internos.
   * **Control de Flujo Funcional:** Uso del monad `Result[T]` (`Result.success` / `Result.failure`) en lugar de excepciones para control de flujo de negocio.
   * **Puertos ACL:** Interfaces abstractas hacia servicios externos en `application/acl/ports/`.
3. **Interface Layer (Capa de Interfaces):**
   * Adaptadores primarios: Controladores REST orientados a objetos con FastAPI.
   * **Assemblers:** Mapeo desacoplado entre esquemas Pydantic v2 (OpenAPI 3.1) y Commands/DTOs del dominio.
4. **Infrastructure Layer (Capa de Infraestructura):**
   * Adaptadores secundarios: Implementación de repositorios desacoplados del modelo de dominio (modelos ORM SQLAlchemy en infraestructura).
   * **Transactional Outbox Pattern:** Persistencia atómica de eventos en tabla `outbox_events` para publicación asíncrona hacia Message Brokers.
   * **Anti-Corruption Layer (ACL):** Adaptadores de traducción para Flight API, pasarelas de pago y proveedores externos, aislando el dominio de modelos de datos foráneos.
   * **Open Host Service (OHS):** Fachadas públicas (`interfaces/acl/facade/`) para la comunicación síncrona segura entre Bounded Contexts dentro del monolito.
   * **Aislamiento Físico de Datos:** Prohibidas las Foreign Keys físicas entre tablas de distintos Bounded Contexts (enlace exclusivo por IDs lógicos).

### 3.2. Diagramas como Código (Diagrams as Code)
* **Domain Layer Class Diagrams:** Diagramas de clases PlantUML (`.puml`) detallando visibilidad, miembros, tipos, multiplicidades y relaciones.
* **Database Diagrams:** Diagramas relacionales de bases de datos PlantUML (`.puml`) con especificación de tablas, tipos de columnas, claves primarias/foráneas y restricciones de integridad.
* **C4 Architecture Diagrams:** Structurizr DSL (`workspace.dsl`) para la vista de contexto, contenedores y componentes del sistema.

### 3.3. Estándar de Frontend y Experiencia de Usuario (Website y Webapp)
* **Website (`navby-website`):** Sitio público estático construido con Astro 5 bajo arquitectura de islas, Tailwind CSS v4, coreografía de animaciones con GSAP 3, desplazamiento suave con Lenis (`@darkroom.engineering/lenis`) y despliegue global en Edge CDN de Vercel ($0 USD/mes).
* **Webapp (`navby-webapp`):** Cliente interactivo (SPA) construido con React 19, TypeScript y Vite 6. Renderizado de mapa plano 2D Web Mercator con MapLibre GL JS y arcos ortodrómicos WebGL con deck.gl (`ArcLayer`). Arquitectura por capas desacoplada (Presentation, Application, Domain, Infrastructure), sidebar izquierda interactiva bidireccional, buscador flotante de ciudades, skeletons adaptativos de carga con boneyard y notificaciones toast reactivas con Sileo. Despliegue estático en Vercel con reglas de reescritura SPA.
* **Backend Platform (`navby-platform`):** Monolito modular en Python 3.12+, FastAPI, uv, PostgreSQL 16, Redis 7 y Caddy 2 orquestado con Docker Compose. Despliegue en Azure VM `Standard_B2s` (2 vCPUs, 4 GB RAM) con aislamiento estricto de red (solo puertos 80, 443 y 22 SSH expuestos) y viabilidad de crédito de $100 USD para >3 meses 24/7 (>6 a 8 meses con Auto-Shutdown).

---

## 4. Flujo de Construcción y Comandos (`Makefile`)

El repositorio compila documentos y diagramas mediante contenedores Docker oficiales (`pandoc/extra:3.8.3`, `ghcr.io/plantuml/plantuml`, `structurizr/structurizr`).

### 4.1. Compilación del Reporte Académico
* **Compilación general:**
  ```bash
  make pdf
  ```
* **Compilación multidioma:**
  ```bash
  make pdf-es   # Metadatos en español (pandoc/lang/es-ES.yaml)
  make pdf-en   # Metadatos en inglés (pandoc/lang/en-US.yaml)
  ```
* **Previsualización de sección individual:**
  ```bash
  make single SRC=report/chapters/10-problem-description/11-context-and-foundation.md
  ```
* **Limpieza de artefactos generados:**
  ```bash
  make clean
  ```

### 4.2. Compilación de Diagramas como Código
* **Diagramas C4 (Structurizr DSL):**
  ```bash
  make c4
  ```
* **Diagramas de Clases (PlantUML):**
  ```bash
  make class-diagrams
  ```
* **Diagramas de Base de Datos (PlantUML):**
  ```bash
  make db-diagrams
  ```
* **Compilación total (diagramas + reporte consolidado):**
  ```bash
  make all
  ```

---

## 5. Estructura del Repositorio y Rangos Numéricos

Para garantizar el ordenamiento determinista en la concatenación de Pandoc (`$(sort ...)`), se utiliza una estructura numerada estricta:

```text
navby-report/
├── docs/                                  # Documentación de ingeniería extendida (Backend, Arquitectura, Guías)
│   ├── backend-documentation/             # Especificaciones tácticas DDD, esquemas BD, arquitectura, FlightAPI
│   ├── frontend-architecture/             # Especificaciones de Frontend (Website Astro y Webapp React/MapLibre)
│   ├── navby-datasets/                    # Datasets depurados definitivos (airports, routes_unique, routes, etc.)
│   ├── guidelines_tables_figures_apa7.md  # Guía de formato APA 7
│   ├── how-to-use.md                      # Manual del entorno de compilación
│   ├── navby-documentation.md             # Biblia de producto, visión funcional y enrutador de verdad
│   └── project-statement.md               # Rúbricas oficiales (Complejidad Algorítmica y Móviles)
├── report/                                # Reporte académico oficial de tesis (Complejidad Algorítmica)
│   ├── front-matter/                      # Rango 01 - 09: Secciones preliminares (carátula, dedicatoria, resumen)
│   ├── chapters/                          # Rango 10 - 89: Capítulos temáticos del cuerpo principal
│   │   ├── 10-problem-description/        #   Capítulo 1 (archivos 11 al 19)
│   │   ├── 20-dataset-description/        #   Capítulo 2 (archivos 21 al 29)
│   │   └── 30-algorithmic-proposal/       #   Capítulo 3 (archivos 31 al 39)
│   ├── back-matter/                       # Rango 90 - 99: Conclusiones, recomendaciones y referencias
│   ├── annexes/                           # Anexos y material suplementario
│   ├── assets/                            # PNGs compilados y diagram-sources/ (C4 DSL, PlantUML)
│   └── bibliography/                      # Fuentes bibliográficas (.bib)
├── pandoc/                                # Plantilla LaTeX (eisvogel), filtros Lua y configuración de idioma
└── Makefile                               # Automatización de tareas y compilación contenerizada
```

---

## 6. Estándares Editoriales y de Redacción Académica (APA 7)

Al redactar o editar documentos en `report/`, es mandatorio acatar las siguientes normas de estilo y moderación visual:

### 6.1. Voz y Tono Académico
* **Perspectiva:** Redactar en tercera persona del plural («el equipo analizó», «se diseñó») o impersonal («se propone»).
* **Prosa continua:** Privilegiar párrafos estructurados y explicativos sobre listas excesivas de viñetas.
* **Prohibición de menciones meta-académicas a la rúbrica:** Queda prohibido escribir expresiones como «según la rúbrica», «en cumplimiento con la rúbrica» o «conforme al criterio de evaluación». Toda decisión técnica debe justificarse por su impacto ingenieril, complejidad algorítmica o requerimiento de la solución.
* **Erradicación de redundancias bilingües:** Prohibidas las aclaraciones entre paréntesis de términos técnicos (ej. «árbol de expansión mínima (*Minimum Spanning Tree*)»). Se utiliza únicamente el término en inglés establecido por la industria o su traducción técnica formal en español, pero nunca ambos a la vez en la misma frase.
* **Supresión de incisos y ejemplos superfluos:** Evitar `(por ejemplo, ...)`, `(ej. ...)`, `(p. ej., ...)` o `(e.g., ...)`. Los paréntesis se reservan exclusivamente para citas bibliográficas APA 7 `(autor, año)`, signaturas de métodos o restricciones numéricas formales.

### 6.2. Moderación Tipográfica y Control de Markdown
* **Sin saturación de comillas invertidas (backticks):**
  * Nombres de clases, agregados y tipos: En **negrita** o texto plano (**Graph**, **FlightNode**).
  * Métodos y operaciones: En *cursiva* con paréntesis (*findShortestPath()*, *calculateHaversineDistance()*).
  * Atributos: En **negrita** o texto plano.
  * Backticks: Reservados para firmas compactas de código, contratos de interfaces con tipos, comandos de consola o rutas de archivo.
* **Tablas APA 7:**
  * **Prioridad a tablas nativas en Markdown:** Emplear sintaxis Markdown estándar para tablas de datos y métricas cuantitativas (`| Columna 1 | Columna 2 |`), con títulos `: Título {#tbl:id}` y notas `*Nota.*`.
  * **Dimensionamiento y alineación por longitud de celda:** La longitud de los guiones en la fila separadora (`:---:`, `:---`) controla proporcionalmente los anchos de columna en Pandoc LaTeX. Columnas con texto breve ($\le 3$ palabras como identificadores, fases o métricas escalares) deben configurarse centradas (`:---:`), mientras que columnas con descripciones narrativas o formulaciones deben alinearse a la izquierda (`:---`) y contar con suficientes guiones para evitar saltos de línea antiestéticos o guionado involuntario de palabras.
  * La primera columna (nombres, clases, identificadores) nunca lleva backticks.
  * No envolver tipos de datos estándar (`String`, `int`, `double`, `UUID`) en backticks si la columna ya los tipifica.
  * Prohibido el uso de punto y coma (`;`) para listar elementos en celdas; utilizar saltos de línea limpios o viñetas con guion (`- `).
  * **Uso exclusivo de LaTeX (`tabularx`):** Reservado únicamente para estructuras complejas con celdas fusionadas (`\multirow`, `\multicolumn`, `\thspan`) o matrices densas que no puedan resolverse limpiamente en Markdown.
* **Notación Matemática:**
  * No usar `$ ... $` para comparaciones o límites escalares triviales; redactar en texto plano: `(*costo* ≥ 0.0)`.
  * Reservar los bloques LaTeX (`$$ ... $$`) para ecuaciones algebraicas formales (fórmula de Haversine, demostración analítica de complejidad asintótica, etc.).
* **Modelado Espacial y Proyección Geodésica:**
  * Las rutas aéreas en Navby se modelan como arcos de círculo máximo (trayectoria ortodrómica) mediante la formulación de Haversine, representando analíticamente la distancia geodésica física mínima en el espacio tridimensional de la Tierra. Su visualización curvada sobre el plano bidimensional (Web Mercator) es consecuencia matemática natural de la proyección cartográfica y modela con exactitud la trayectoria real de vuelo frente a líneas rectas planas (loxodrómicas).

---

## 7. Reglas del Entorno de Desarrollo y Herramientas

* **Gestor de Paquetes Node.js Exclusivo (pnpm):** En caso de requerir utilidades de Node.js, utilizar estrictamente `pnpm` (`pnpm install`, `pnpm add`, `pnpm run <script>`). Queda terminantemente prohibido el uso de `npm` y `yarn`.
* **Ejecución Remota Node.js:** Utilizar siempre `pnpm dlx` en lugar de `npx`.
* **Entorno y Gestor de Paquetes Python (uv):** Para el desarrollo del backend en Python 3.12+, utilizar exclusivamente **`uv`** (`uv venv`, `uv pip install`, `uv run`) como estándar ultrarrápido y determinista.
* **Comandos Slash Nativos:** Los flujos y automatizaciones personalizadas (como `/commit` o `/review`) se ejecutan siguiendo las instrucciones de `~/.gemini/config/commands/`. No se utiliza OpenCode.
* **Entorno de Agente:** Configurado nativamente para interactuar con herramientas del ecosistema Google Gemini / Antigravity CLI.

---

## 8. Habilidades (Skills) Especializadas

* `academic-report-writer`: Directrices académicas para la redacción y edición de capítulos en `report/`.
* `academic-report-reviewer`: Auditoría, detección de exceso de backticks y control de calidad editorial APA 7.
* `docs-writer`: Estándares de redacción técnica para archivos `.md` y la carpeta `docs/`.
* `architecture-patterns`: Patrones de arquitectura limpia, hexagonal y diseño desacoplado.
* `ddd-strategic-design` & `domain-modeling`: Modelado estratégico y táctico de Bounded Contexts y lenguaje ubicuo.
* `postgres` & `redis-core`: Estándares de modelado para persistencia relacional y almacenamiento de claves en memoria.
