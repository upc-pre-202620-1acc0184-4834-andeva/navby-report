# Documentación de Navby

Navby recomienda los 3 mejores vuelos entre dos ciudades combinando precio, duración y escalas en un único puntaje. Esta carpeta contiene la documentación de producto e ingeniería. El informe académico vive aparte, en [`report/`](../report/).

## Orden de lectura

1. [navby-documentation.md](navby-documentation.md): **fuente de verdad del producto**. Contiene las reglas, los algoritmos, los créditos y el alcance.
2. [backend-documentation/navby-platform-documentation.md](backend-documentation/navby-platform-documentation.md): arquitectura del backend y mapa de bounded contexts.
3. El documento del bounded context que vayas a tocar (tabla de abajo).

## Mapa

| Documento | Contenido |
| :--- | :--- |
| [navby-documentation.md](navby-documentation.md) | Producto, flujo de búsqueda, BFS, A\*, motor multicriterio, reglas de negocio, créditos y alcance. |
| [product-marketing.md](product-marketing.md) | Posicionamiento, buyer personas y mensajes comerciales. |
| **Backend** | |
| [navby-platform-documentation.md](backend-documentation/navby-platform-documentation.md) | Stack, capas, estructura de carpetas, bounded contexts, mapa de contextos y despliegue. |
| [navby-backend-tactical-specification.md](backend-documentation/navby-backend-tactical-specification.md) | Convenciones de código: reglas de arquitectura, Shared Kernel, `Result`, errores y outbox. |
| [navby-endpoints.md](backend-documentation/navby-endpoints.md) | Catálogo de endpoints REST con contratos de entrada y salida. |
| [navby-database-schema.md](backend-documentation/navby-database-schema.md) | DDL de PostgreSQL 16 y claves de Redis 7. |
| [flight-api-documentation.md](backend-documentation/flight-api-documentation.md) | Integración con FlightAPI. |
| [navby-environments-and-deployment.md](backend-documentation/navby-environments-and-deployment.md) | Dominios (`navby.andeva.tech`, `/app`, `/api`), entornos, secretos y despliegue continuo. |
| [navby-datasets/README.md](backend-documentation/navby-datasets/README.md) | Datasets de OpenFlights y pipeline de depuración. |
| **Bounded contexts** | |
| [bounded-context-shared.md](backend-documentation/extended-bounded-contexts-description/bounded-context-shared.md) | Shared Kernel: clases base, `Result`, outbox, errores y rate limiting. |
| [bounded-context-iam.md](backend-documentation/extended-bounded-contexts-description/bounded-context-iam.md) | Registro con términos, verificación de correo, login local y con Google, sesiones, recuperación de contraseña y eliminación de cuenta. |
| [bounded-context-routing.md](backend-documentation/extended-bounded-contexts-description/bounded-context-routing.md) | Grafo en memoria, BFS, A\*, catálogo de ciudades y vista previa de ruta. |
| [bounded-context-quotes.md](backend-documentation/extended-bounded-contexts-description/bounded-context-quotes.md) | FlightAPI, caché, motor multicriterio y podio. |
| [bounded-context-billing.md](backend-documentation/extended-bounded-contexts-description/bounded-context-billing.md) | Billetera, créditos diarios, paquetes y Mercado Pago. |
| [bounded-context-itineraries.md](backend-documentation/extended-bounded-contexts-description/bounded-context-itineraries.md) | Guardar, listar, ver y eliminar ofertas del podio. |
| **Backlog** | |
| [user-stories.md](backlog/user-stories.md) | Historias de usuario con criterios de aceptación en Gherkin (comportamiento, sin diseño). |
| [technical-stories.md](backlog/technical-stories.md) | Historias técnicas: una por endpoint y por tarea de plataforma. |
| **Frontend** | |
| [navby-webapp-documentation.md](frontend-documentation/navby-webapp-documentation.md) | Webapp React: flujo de búsqueda, mapa, podio y librerías. |
| [navby-website-documentation.md](frontend-documentation/navby-website-documentation.md) | Website Astro: herramientas, i18n y accesibilidad. |
| [design-system.md](frontend-documentation/design-system.md) | Paleta, tipografía, logos y tokens CSS. |
| **Académico** | |
| [project-statement.md](project-statement.md) | Rúbricas oficiales del curso (no se edita). |
| [report-guidelines.md](report-guidelines.md) | Plantilla del informe APA 7 y entorno Docker. |
| [tables-figures-apa-7-guidelines.md](tables-figures-apa-7-guidelines.md) | Estándar de tablas y figuras APA 7. |
| [Optimización de Itinerarios Aéreos.md](<Optimización de Itinerarios Aéreos.md>) | Investigación de antecedentes y referencias para el capítulo 1 del informe. |

## Reglas de mantenimiento

- **Un dato, un lugar.** Las reglas de negocio y los números (créditos, pesos, límites, TTL) se definen en `navby-documentation.md`. Los demás documentos los referencian por ID (`RN-08`) en lugar de repetirlos.
- **Nada fuera de alcance.** Si una función no aparece en la sección 10 de `navby-documentation.md`, no se documenta.
- **Idioma.** Español. Los nombres de clases, endpoints y código van en inglés.
