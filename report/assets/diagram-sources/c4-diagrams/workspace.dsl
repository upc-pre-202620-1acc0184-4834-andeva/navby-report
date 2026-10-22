workspace "Navby" "Arquitectura del Sistema de Recomendacion y Enrutamiento Inteligente de Vuelos Navby" {

    model {
        !include model/actors.dsl
        !include model/external-systems.dsl
        !include model/systems/bussiness-core.dsl

        viajero -> webapp "Interactua con el buscador, mapa cartografico y podio" "HTTPS"
    }

    views {
        !include views/context-views.dsl
        !include views/container-views.dsl

        styles {
            element "Person" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "WebBrowser" {
                shape WebBrowser
                background #438DD5
                color #ffffff
            }
            element "API" {
                shape RoundedBox
                background #2A6496
                color #ffffff
            }
            element "Engine" {
                shape Component
                background #604AFF
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #2A6496
                color #ffffff
            }
            element "External" {
                background #707070
                color #ffffff
            }
        }
    }
}
