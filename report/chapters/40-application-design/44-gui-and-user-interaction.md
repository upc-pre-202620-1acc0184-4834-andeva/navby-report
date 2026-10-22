## 4.4. Diseño de Interfaz Gráfica y Experiencia de Usuario

La interfaz gráfica de usuario (GUI) de Navby está concebida para materializar los resultados de los algoritmos de grafos sobre un entorno visual accesible e intuitivo, abstrayendo la complejidad matemática de la optimización multiobjetivo. La aplicación cliente se estructura como una aplicación de página única (SPA) interactiva desarrollada en React y TypeScript.

En la @tbl:componentes-gui se describen los principales componentes visuales de la interfaz de usuario y su interacción con los algoritmos del sistema.

| Módulo Visual | Tecnología | Interacción Algorítmica | Propósito en la Experiencia de Usuario |
| :---: | :---: | :---: | :--- |
| Buscador de Ciudades | React, TanStack Query | `GET /routing/cities` | Autocompletado de ciudades con resolución automática de aeropuertos metropolitanos. |
| Visor Cartográfico 2D | MapLibre GL, deck.gl | `GET /routing/preview` | Renderizado inmediato de arcos geodésicos ortodrómicos para la ruta preliminar de A\*. |
| Panel Lateral del Podio | React, Tailwind CSS | `POST /quotes/search` | Visualización comparativa de las tres ofertas ganadoras con afinidad, precio, escalas y deep link. |
| Control de Preferencias | React, Zustand | Reordenamiento local | Ajuste de ponderaciones $(\alpha, \beta, \gamma)$ para reordenar la frontera de Pareto sin recotizar. |

: Componentes Principales de la Interfaz Gráfica de Usuario {#tbl:componentes-gui}

*Nota.* Componentes de presentación e interacción desarrollados para la visualización del grafo y las recomendaciones.

### 4.4.1. Visualización Cartográfica de Rutas sobre el Grafo

El visor cartográfico proyecta la red de vuelos sobre un mapa plano bidimensional en proyección Web Mercator utilizando MapLibre GL JS y deck.gl. Para reflejar la física del transporte aéreo, las trayectorias entre aeropuertos se trazan como arcos de círculo máximo (curvas ortodrómicas) mediante capas WebGL especializadas.

El sistema proporciona retroalimentación visual progresiva en dos tiempos:

1. **Ruta Preliminar Inmediata:** Al enviar el formulario de búsqueda, el mapa recibe la respuesta de vista previa de rutas en menos de 50 milisegundos y dibuja de inmediato la secuencia de aeropuertos de la ruta más rápida calculada por A\*, acompañada de la duración física mínima ($T_{\min}$).
2. **Despliegue del Podio Definitivo:** Una vez concluido el proceso de cotización y filtrado de Pareto, la ruta preliminar se desvanece de forma suave y se proyectan las tres rutas comerciales definitivas con códigos de color diferenciados según su posición en el podio.

### 4.4.2. Presentación del Podio y Reordenamiento de Preferencias

El panel lateral izquierdo organiza las tres recomendaciones finales en tarjetas estructuradas de acuerdo a su puntaje de equilibrio. Cada tarjeta presenta el porcentaje de afinidad $(1 - S) \times 100\%$, el desglose de tramos y escalas, la aerolínea operadora, el precio final consolidado y el tiempo adicional respecto al mínimo físico ($+X\text{ h sobre } T_{\min}$). Al interactuar con el cursor sobre una tarjeta, el mapa resalta la trayectoria ortodrómica correspondiente.

Asimismo, la interfaz incorpora controles deslizantes interactivos para los pesos de precio, duración y escalas. Como la frontera de Pareto es invariable respecto a los pesos de la función de utilidad, modificar estos valores recalcula el puntaje $S$ y reordena el podio de forma instantánea en memoria del navegador, sin generar nuevas consultas a la red ni consumir créditos del usuario.

\newpage
