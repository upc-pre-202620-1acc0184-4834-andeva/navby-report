container navbySystem "Containers" "Diagrama de Contenedores de la Plataforma Navby" {
    include *
    autoLayout lr
}

dynamic navbySystem "SearchSequence" "Diagrama de Secuencia de una Busqueda de Vuelos" {
    webapp -> apiPlatform "1. POST /quotes/search (criterios de viaje)"
    apiPlatform -> routingEngine "2. select_pairs(origen, destino) [BFS + A*]"
    routingEngine -> apiPlatform "3. Pares alcanzables <= 2 escalas + T_min"
    apiPlatform -> redisCache "4. Consulta cache por par"
    apiPlatform -> flightApi "5. Consulta ofertas comerciales sin cache (max 2)"
    flightApi -> apiPlatform "6. Retorna ofertas vigentes"
    apiPlatform -> quotesEngine "7. Filtrado de Pareto y puntaje multicriterio"
    quotesEngine -> apiPlatform "8. Podio Top 3 de ofertas"
    apiPlatform -> webapp "9. Responde podio con coordenadas y deep links"
    autoLayout lr
}
