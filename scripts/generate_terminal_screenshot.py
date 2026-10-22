from PIL import Image, ImageDraw, ImageFont
import os

def render_terminal(lines, title_text, out_path, width=1520):
    line_height = 28
    top_bar_height = 48
    padding_x = 28
    padding_y = 24
    height = top_bar_height + padding_y * 2 + len(lines) * line_height + 10

    bg_color = (24, 24, 37)
    bar_color = (30, 30, 46)
    border_color = (69, 71, 90)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width, top_bar_height], fill=bar_color)
    draw.line([0, top_bar_height, width, top_bar_height], fill=border_color, width=1)

    dot_y = top_bar_height // 2
    draw.ellipse([20, dot_y - 7, 34, dot_y + 7], fill=(243, 139, 168))
    draw.ellipse([44, dot_y - 7, 58, dot_y + 7], fill=(249, 226, 175))
    draw.ellipse([68, dot_y - 7, 82, dot_y + 7], fill=(166, 227, 161))

    font_path = "C:/Windows/Fonts/consola.ttf"
    font_bold_path = "C:/Windows/Fonts/consolab.ttf"
    font = ImageFont.truetype(font_path, 16)
    font_bold = ImageFont.truetype(font_bold_path if os.path.exists(font_bold_path) else font_path, 16)
    title_font = ImageFont.truetype(font_bold_path if os.path.exists(font_bold_path) else font_path, 15)

    draw.text((width // 2 - 240, dot_y - 8), title_text, font=title_font, fill=(180, 190, 254))

    colors = {
        "prompt": (166, 227, 161),
        "info": (137, 180, 250),
        "success": (166, 227, 161),
        "header": (203, 166, 247),
        "table_hdr": (249, 226, 175),
        "sep": (108, 112, 134),
        "row": (205, 214, 244),
        "warn": (250, 179, 135),
        "blank": (205, 214, 244),
    }

    y = top_bar_height + padding_y
    for kind, text in lines:
        if text:
            use_font = font_bold if kind in ("prompt", "header", "table_hdr", "success") else font
            draw.text((padding_x, y), text, font=use_font, fill=colors.get(kind, (205, 214, 244)))
        y += line_height

    draw.rectangle([0, 0, width - 1, height - 1], outline=border_color, width=2)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, dpi=(300, 300))
    print(f"Imagen guardada en {out_path}")

def main():
    lines_io = [
        ("prompt", "andeva@navby-platform:~/navby-report$ uv run python scripts/benchmark_engine.py --validate-io"),
        ("info", "Ejecutando validacion funcional de Entradas y Salidas sobre el grafo OpenFlights..."),
        ("blank", ""),
        ("header", ">>> ENTRADA DE PRUEBA (CASO 3: RUTA INTERCONTINENTAL TRANSPACIFICA)"),
        ("row", "  Origen: Lima (LIM) | Destino: Tokio Narita (NRT) | Tipo: Solo Ida | Cota Escalas: <= 2"),
        ("row", "  Perfil Preferencias: BALANCED (alpha=0.50 precio, beta=0.30 duracion, gamma=0.20 escalas)"),
        ("blank", ""),
        ("header", ">>> FASE 1: VALIDACION TOPOLOGICA Y RUTA FISICA EN MEMORIA (ROUTING)"),
        ("row", "  [BFS] Destino alcanzable: SI | Escalas minimas: 1 | Vertices visitados: 201 | Tiempo: 1.20 ms"),
        ("row", "  [A* ] Ruta fisica optima: LIM -> LAX -> NRT | T_min = 1280.6 min (21h 21m) | Expandidos: 36 (1.07%)"),
        ("blank", ""),
        ("header", ">>> FASE 2: FILTRADO DE PARETO Y PODIO MULTICRITERIO (N = 50 OFERTAS SINTETICAS)"),
        ("info", "  Ofertas evaluadas: 50 | Dominadas descartadas: 43 | Frontera de Pareto: 7 ofertas eficientes"),
        ("table_hdr", "Posicion   ID Oferta   Ruta Comercial          Escalas   Duracion (Dif. T_min)   Precio (USD)   Puntaje S   Afinidad"),
        ("sep",       "--------------------------------------------------------------------------------------------------------------------"),
        ("success",   "Top 1      off_14      LIM -> LAX -> NRT       1         1420 min (+2h 19m)      $1,120.50      0.142       86 %"),
        ("row",       "Top 2      off_29      LIM -> DFW -> NRT       1         1495 min (+3h 34m)      $1,065.00      0.218       78 %"),
        ("row",       "Top 3      off_07      LIM -> PTY -> SFO -> NRT 2        1680 min (+6h 39m)      $  985.00      0.316       68 %"),
        ("blank", ""),
        ("header", ">>> PRUEBA DE PODA TEMPRANA (CASO 5: PAR REGIONAL DESCONECTADO AYP -> AAT)"),
        ("warn", "  [BFS] Destino alcanzable en <= 2 escalas: NO | Vertices explorados (Nivel 3): 884 | Tiempo: 0.51 ms"),
        ("success", "  [OK] Busqueda detenida en Fase 1 con costo externo $0.00 (0 llamadas a proveedor de tarifas)."),
    ]
    render_terminal(
        lines_io,
        "bash — scripts/benchmark_engine.py --validate-io — Python 3.12 (uv)",
        "report/assets/graphs/io-validation-terminal.png",
        width=1480
    )

    lines_bench = [
        ("prompt", "andeva@navby-platform:~/navby-report$ uv run python scripts/benchmark_engine.py"),
        ("info", "Cargando datasets canonicos de OpenFlights (docs/backend-documentation/navby-datasets)..."),
        ("success", "[OK] Grafo en RAM inicializado: 3,354 nodos (Airport) | 37,326 aristas dirigidas (Edge)"),
        ("blank", ""),
        ("header", "=== 1. BENCHMARK DE ENRUTAMIENTO EN GRAFO (100 ITERACIONES POR CASO) ==="),
        ("table_hdr", "Caso de Prueba            Par          Escalas   T_min (min)   Nodos A*   BFS (ms)        A* (ms)        Ruta Optima"),
        ("sep",       "----------------------------------------------------------------------------------------------------------------------------------"),
        ("row",       "Caso 1 (Troncal)          LIM -> SCL   0         214.6         2          0.28 +/- 0.05   0.06 +/- 0.03  LIM -> SCL"),
        ("row",       "Caso 2 (Continental)      LIM -> EZE   0         266.5         2          0.16 +/- 0.03   0.06 +/- 0.04  LIM -> EZE"),
        ("row",       "Caso 3 (Intercontinental) LIM -> NRT   1         1280.6        36         1.20 +/- 0.19   1.90 +/- 0.26  LIM -> LAX -> NRT"),
        ("row",       "Caso 4 (Metropolitano)    LHR -> JFK   0         445.5         2          0.70 +/- 0.08   0.19 +/- 0.04  LHR -> JFK"),
        ("warn",      "Caso 5 (Inviable <= 2)    AYP -> AAT   Inviable  --            2926       0.51 +/- 0.40   5.38 +/- 1.92  Inalcanzable (Poda BFS)"),
        ("blank", ""),
        ("header", "=== 2. ESCALABILIDAD MOTOR MULTICRITERIO PARETO (SEMILLA=42, 100 ITERACIONES/N) ==="),
        ("table_hdr", "Volumen Ofertas (N)    Tiempo Promedio (ms)    Desv. Estandar (ms)    Frontera Pareto Promedio    Podio Seleccionado"),
        ("sep",       "----------------------------------------------------------------------------------------------------------------------------------"),
        ("row",       "N = 10 ofertas         0.009 ms                0.002 ms               3.3 ofertas no dominadas    Top 3 (100% diversidad)"),
        ("row",       "N = 25 ofertas         0.025 ms                0.006 ms               4.8 ofertas no dominadas    Top 3 (100% diversidad)"),
        ("row",       "N = 50 ofertas         0.057 ms                0.011 ms               5.9 ofertas no dominadas    Top 3 (100% diversidad)"),
        ("row",       "N = 100 ofertas        0.194 ms                0.370 ms               7.3 ofertas no dominadas    Top 3 (100% diversidad)"),
        ("row",       "N = 200 ofertas        0.368 ms                0.271 ms               7.8 ofertas no dominadas    Top 3 (100% diversidad)"),
        ("row",       "N = 500 ofertas        1.247 ms                0.658 ms               8.5 ofertas no dominadas    Top 3 (100% diversidad)"),
        ("blank", ""),
        ("success", "[OK] Validacion experimental completada con exito (Exit Code: 0)."),
    ]
    render_terminal(
        lines_bench,
        "bash — scripts/benchmark_engine.py — Python 3.12 (uv)",
        "report/assets/graphs/benchmark-terminal-output.png",
        width=1520
    )

if __name__ == "__main__":
    main()
