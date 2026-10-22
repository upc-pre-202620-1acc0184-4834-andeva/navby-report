navbySystem = softwareSystem "Plataforma Navby" "Sistema de enrutamiento inteligente de vuelos y optimizacion multicriterio." {
    webapp = container "Aplicacion Web Interactiva (SPA)" "Proporciona la interfaz de usuario, buscador de ciudades, mapa plano 2D y panel del podio." "React 19, TypeScript, MapLibre GL, deck.gl" "WebBrowser"
    
    apiPlatform = container "Plataforma Backend API" "Monolito modular asincrono que orquesta las solicitudes y expone endpoints REST." "Python 3.12+, FastAPI, Uvicorn" "API"
    
    routingEngine = container "Motor de Rutas (RAM)" "Mantiene el grafo en memoria de 3,354 aeropuertos y ejecuta BFS (poda) y A* (T_min)." "Estructuras nativas de Python" "Engine"
    
    quotesEngine = container "Motor de Cotizaciones y Podio" "Filtra la frontera de Pareto, normaliza criterios y calcula el ranking multicriterio Top 3." "Python, NumPy" "Engine"
    
    redisCache = container "Cache Efimera y Sesiones" "Almacena temporalmente cotizaciones de vuelos (TTL 30 min) y control de sesiones." "Redis 7" "Database"
    
    postgresDb = container "Base de Datos Relacional" "Persiste de forma durable cuentas de usuario, saldo de creditos e itinerarios guardados." "PostgreSQL 16" "Database"

    # Relaciones internas de contenedores
    webapp -> apiPlatform "Envia peticiones de ruta y cotizaciones via REST" "JSON/HTTPS"
    apiPlatform -> webapp "Responde podio con coordenadas y deep links" "JSON/HTTPS"
    apiPlatform -> routingEngine "Verifica viabilidad con BFS y ruta minima con A*" "Llamada en RAM"
    routingEngine -> apiPlatform "Retorna pares alcanzables y T_min" "Llamada en RAM"
    apiPlatform -> quotesEngine "Solicita calculo de Pareto y ordenamiento de podio" "Llamada en RAM"
    quotesEngine -> apiPlatform "Retorna podio Top 3 de ofertas" "Llamada en RAM"
    apiPlatform -> redisCache "Consulta y almacena cotizaciones en cache (TTL 30 min)" "RESP/TCP"
    redisCache -> apiPlatform "Retorna cotizaciones cacheadas" "RESP/TCP"
    quotesEngine -> redisCache "Verifica y almacena cotizaciones en cache (TTL 30 min)" "RESP/TCP"
    quotesEngine -> flightApi "Consulta ofertas comerciales no cacheadas (max 2 pares)" "HTTPS/JSON"
    apiPlatform -> flightApi "Consulta ofertas comerciales no cacheadas (max 2 pares)" "HTTPS/JSON"
    flightApi -> apiPlatform "Retorna ofertas comerciales vigentes" "HTTPS/JSON"
    apiPlatform -> postgresDb "Persiste usuarios, saldo de creditos e itinerarios" "asyncpg / TCP"
    apiPlatform -> mercadoPago "Procesa recargas de paquetes de creditos" "HTTPS/REST"
    apiPlatform -> googleAuth "Valida tokens de identidad federada" "HTTPS"
    apiPlatform -> resendService "Despacha correos con enlaces y codigos OTP" "HTTPS/REST"
}
