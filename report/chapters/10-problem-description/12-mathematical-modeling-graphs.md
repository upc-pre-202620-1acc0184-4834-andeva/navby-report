## 1.2. Formalización Matemática del Grafo Aéreo

La red aerocomercial se modela formalmente como un grafo dirigido y ponderado $G = (V, E, W)$. El conjunto de vértices $V$ representa las terminales aeroportuarias comerciales georreferenciadas mediante coordenadas geográficas expresadas en latitud ($\phi_u$) y longitud ($\lambda_u$) bajo el elipsoide WGS84, junto a su código canónico IATA, consolidando $|V| = 3,354$ nodos comerciales activos. El conjunto de aristas dirigidas $E \subseteq V \times V$ modela las rutas directas programadas entre un aeropuerto origen $u$ y un destino $v$, totalizando $|E| = 37,326$ conexiones operativas únicas.

Dado que la base topológica no incluye horarios ni frecuencias dinámicas, la distancia física ortodrómica mínima entre terminales sobre la superficie esférica terrestre se determina mediante la formulación trigonométrica de Haversine:

$$d_H(u, v) = 2 R \arcsin \left( \sqrt{ \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_u) \cos(\phi_v) \sin^2\left(\frac{\Delta \lambda}{2}\right) } \right)$$

En esta ecuación, $R \approx 6,371\text{ km}$ denota el radio medio terrestre, $\Delta \phi = \phi_v - \phi_u$ representa la diferencia de latitud angular entre el aeropuerto de destino $v$ y el de origen $u$, y $\Delta \lambda = \lambda_v - \lambda_u$ define la diferencia angular de longitud entre ambas terminales.

La función de ponderación $W: E \to \mathbb{R}^+$ asigna a cada arco dirigido $(u, v) \in E$ un costo que modela el tiempo estimado de vuelo continuo entre ambas terminales a partir de su distancia geodésica:

$$w_t(u, v) = \frac{d_H(u, v)}{v_{\text{crucero}}} + t_{\text{maniobra}}$$

Para este cálculo se adopta una velocidad de crucero constante de 800 km/h ($v_{\text{crucero}}$) y un tiempo adicional de maniobra de 30 minutos ($t_{\text{maniobra}}$), el cual contempla las fases operativas obligatorias de rodaje en pista, despegue, ascenso, descenso y aproximación terminal.

La conectividad de la red es muy desigual. Cada aeropuerto tiene en promedio 11.13 rutas salientes (22.26 si se suman las entrantes), mientras que los principales centros de conexión superan las 230 rutas salientes [@wandelt2025network]. Esta concentración en pocos aeropuertos centrales es la que permite unir casi cualquier par de ciudades con pocas escalas, y es también la que hace crecer rápidamente el número de combinaciones posibles al explorar la red.

\newpage
