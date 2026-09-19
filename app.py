import streamlit as st
from best_tracks import descargar_hurdat, buscar_ciclon
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import folium
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import unary_union
from streamlit_folium import st_folium
import json
from branca.element import Element

st.set_page_config(
    page_title="Simulador de Huracanes NHC",
    layout="wide"
)

st.title("🌀 Simulador Académico de Huracanes (Estilo NHC)")

st.sidebar.header("Parámetros del Ciclón")

modo = st.sidebar.radio(
    "Modo de simulación",
    ["Huracán hipotético", "Ciclón tropical histórico"]
)

name = st.sidebar.text_input(
    "Nombre de la Tormenta",
    value="ALBERTO"
)

if modo == "Ciclón tropical histórico":
    ciclón = st.sidebar.selectbox(
        "Ciclón histórico",
        [
            "Irma (2017)",
            "María (2017)",
            "Fiona (2022)",
            "Lenny (1999)",
            "Jeanne (2004)",
            "Irene (2011)",
            "Erin (2007)",
            "Ernesto (2024)"
        ]
    )

if modo == "Ciclón tropical histórico":

    datos_hurdat = descargar_hurdat()

    datos_ciclon = buscar_ciclon(
        datos_hurdat,
        ciclón.split(" (")[0]
    )

    posiciones = datos_ciclon[1:]

    opciones_posicion = []

    for linea in posiciones:

        partes = linea.split(",")

        if len(partes) >= 7:

            fecha = partes[0].strip()
            hora = partes[1].strip()
            lat_hurdat = partes[4].strip()
            lon_hurdat = partes[5].strip()

            opciones_posicion.append(
                f"{fecha} {hora} UTC — "
                f"{lat_hurdat}, {lon_hurdat}"
            )

    posicion = st.sidebar.selectbox(
        "Posición histórica",
        opciones_posicion
    )

    partes_posicion = posicion.split("—")

    coordenadas = (
        partes_posicion[1]
        .strip()
        .split(",")
    )

    lat_text = coordenadas[0].strip()
    lon_text = coordenadas[1].strip()

    if lat_text.endswith("N"):

        lat = float(
            lat_text[:-1]
        )

    elif lat_text.endswith("S"):

        lat = -float(
            lat_text[:-1]
        )

    else:

        lat = float(
            lat_text
        )

    if lon_text.endswith("W"):

        lon = -float(
            lon_text[:-1]
        )

    elif lon_text.endswith("E"):

        lon = float(
            lon_text[:-1]
        )

    else:

        lon = float(
            lon_text
        )

if modo == "Huracán hipotético":

    lat = st.sidebar.number_input(
        "Latitud Inicial (°N)",
        min_value=10.0,
        max_value=35.0,
        value=20.0,
        step=0.0001,
        format="%.4f"
    )

    lon = st.sidebar.number_input(
        "Longitud Inicial (°W)",
        min_value=-98.0,
        max_value=-40.0,
        value=-70.0,
        step=0.0001,
        format="%.4f"
    )

wind_speed = st.sidebar.slider(
    "Vientos Sostenidos (nudos)",
    min_value=30,
    max_value=165,
    value=75,
    step=5
)

heading = st.sidebar.slider(
    "Rumbo (°)",
    min_value=0,
    max_value=360,
    value=290,
    step=5
)

forward_speed = st.sidebar.slider(
    "Velocidad de Avance (kt)",
    min_value=5,
    max_value=25,
    value=12,
    step=1
)

st.sidebar.markdown("---")

st.sidebar.header(
    "Wind Radii"
)

st.sidebar.subheader(
    "34 kt — Tormenta Tropical"
)

r34_ne = st.sidebar.number_input(
    "34 kt — NE",
    min_value=0.0,
    max_value=500.0,
    value=120.0,
    step=5.0
)

r34_se = st.sidebar.number_input(
    "34 kt — SE",
    min_value=0.0,
    max_value=500.0,
    value=100.0,
    step=5.0
)

r34_sw = st.sidebar.number_input(
    "34 kt — SW",
    min_value=0.0,
    max_value=500.0,
    value=80.0,
    step=5.0
)

r34_nw = st.sidebar.number_input(
    "34 kt — NW",
    min_value=0.0,
    max_value=500.0,
    value=100.0,
    step=5.0
)

st.sidebar.subheader(
    "50 kt"
)

r50_ne = st.sidebar.number_input(
    "50 kt — NE",
    min_value=0.0,
    max_value=400.0,
    value=70.0,
    step=5.0
)

r50_se = st.sidebar.number_input(
    "50 kt — SE",
    min_value=0.0,
    max_value=400.0,
    value=60.0,
    step=5.0
)

r50_sw = st.sidebar.number_input(
    "50 kt — SW",
    min_value=0.0,
    max_value=400.0,
    value=45.0,
    step=5.0
)

r50_nw = st.sidebar.number_input(
    "50 kt — NW",
    min_value=0.0,
    max_value=400.0,
    value=60.0,
    step=5.0
)

st.sidebar.subheader(
    "64 kt — Huracán"
)

r64_ne = st.sidebar.number_input(
    "64 kt — NE",
    min_value=0.0,
    max_value=300.0,
    value=35.0,
    step=5.0
)

r64_se = st.sidebar.number_input(
    "64 kt — SE",
    min_value=0.0,
    max_value=300.0,
    value=30.0,
    step=5.0
)

r64_sw = st.sidebar.number_input(
    "64 kt — SW",
    min_value=0.0,
    max_value=300.0,
    value=20.0,
    step=5.0
)

r64_nw = st.sidebar.number_input(
    "64 kt — NW",
    min_value=0.0,
    max_value=300.0,
    value=30.0,
    step=5.0
)


def get_category(wind):

    if wind < 34:

        return "Depresión Tropical"

    elif wind < 64:

        return "Tormenta Tropical"

    elif wind < 83:

        return "Huracán Cat 1"

    elif wind < 96:

        return "Huracán Cat 2"

    elif wind < 113:

        return "Huracán Cat 3 (Mayor)"

    elif wind < 137:

        return "Huracán Cat 4 (Mayor)"

    else:

        return "Huracán Cat 5 (Mayor)"


category_str = get_category(
    wind_speed
)


def create_wind_field(
    center_lon,
    center_lat,
    radii
):

    quadrant_radii = np.array(
        radii,
        dtype=float
    )

    angles = np.linspace(
        0,
        360,
        361
    )

    interpolated_radii = []

    for angle in angles[:-1]:

        if angle >= 315 or angle < 45:

            r1 = quadrant_radii[3]
            r2 = quadrant_radii[0]

            if angle >= 315:

                t = (
                    angle - 315
                ) / 90

            else:

                t = (
                    angle + 45
                ) / 90

        elif angle < 135:

            r1 = quadrant_radii[0]
            r2 = quadrant_radii[1]

            t = (
                angle - 45
            ) / 90

        elif angle < 225:

            r1 = quadrant_radii[1]
            r2 = quadrant_radii[2]

            t = (
                angle - 135
            ) / 90

        else:

            r1 = quadrant_radii[2]
            r2 = quadrant_radii[3]

            t = (
                angle - 225
            ) / 90

        t = np.clip(
            t,
            0,
            1
        )

        smooth_t = (
            1
            - np.cos(
                np.pi * t
            )
        ) / 2

        radius = (
            r1 * (1 - smooth_t)
            +
            r2 * smooth_t
        )

        interpolated_radii.append(
            radius
        )

    interpolated_radii = np.array(
        interpolated_radii
    )

    lat_deg = (
        interpolated_radii
        / 60.0
    )

    lon_deg = (
        interpolated_radii
        /
        (
            60.0
            *
            np.cos(
                np.radians(
                    center_lat
                )
            )
        )
    )

    math_angles = np.radians(
        90 - angles[:-1]
    )

    x = (
        center_lon
        +
        lon_deg
        *
        np.cos(
            math_angles
        )
    )

    y = (
        center_lat
        +
        lat_deg
        *
        np.sin(
            math_angles
        )
    )

    coordinates = np.column_stack(
        (x, y)
    )

    return Polygon(
        coordinates
    )


def calcular_viento_en_punto(
    point_lat,
    point_lon,
    future_lat,
    future_lon,
    wind_speed,
    r34_ne,
    r34_se,
    r34_sw,
    r34_nw,
    r50_ne,
    r50_se,
    r50_sw,
    r50_nw,
    r64_ne,
    r64_se,
    r64_sw,
    r64_nw
):

    lat_diff = (
        point_lat
        -
        future_lat
    )

    lon_diff = (
        point_lon
        -
        future_lon
    )

    distance_nm = np.sqrt(
        (lat_diff * 60.0) ** 2
        +
        (
            lon_diff
            *
            60.0
            *
            np.cos(
                np.radians(
                    future_lat
                )
            )
        ) ** 2
    )

    angle = np.degrees(
        np.arctan2(
            lon_diff
            *
            np.cos(
                np.radians(
                    future_lat
                )
            ),
            lat_diff
        )
    )

    if angle < 0:

        angle += 360

    if 0 <= angle < 90:

        quadrant = "NE"

        r34 = r34_ne
        r50 = r50_ne
        r64 = r64_ne

    elif 90 <= angle < 180:

        quadrant = "SE"

        r34 = r34_se
        r50 = r50_se
        r64 = r64_se

    elif 180 <= angle < 270:

        quadrant = "SW"

        r34 = r34_sw
        r50 = r50_sw
        r64 = r64_sw

    else:

        quadrant = "NW"

        r34 = r34_nw
        r50 = r50_nw
        r64 = r64_nw

    if distance_nm <= r64 and r64 > 0:

        fraction = (
            distance_nm
            /
            r64
        )

        estimated_wind = (
            wind_speed
            -
            (
                (wind_speed - 64)
                *
                fraction
            )
        )

    elif distance_nm <= r50 and r50 > r64:

        fraction = (
            distance_nm
            -
            r64
        ) / (
            r50
            -
            r64
        )

        estimated_wind = (
            64
            -
            (
                14
                *
                fraction
            )
        )

    elif distance_nm <= r34 and r34 > r50:

        fraction = (
            distance_nm
            -
            r50
        ) / (
            r34
            -
            r50
        )

        estimated_wind = (
            50
            -
            (
                16
                *
                fraction
            )
        )

    elif distance_nm <= r34 and r34 > 0:

        estimated_wind = 34

    else:

        if r34 > 0:

            estimated_wind = (
                34
                *
                max(
                    0,
                    1
                    -
                    (
                        distance_nm
                        -
                        r34
                    )
                    /
                    50
                )
            )

        else:

            estimated_wind = 0

    estimated_wind = max(
        0,
        min(
            wind_speed,
            estimated_wind
        )
    )

    return (
        estimated_wind,
        distance_nm,
        quadrant
    )


# ==========================================================
# TRAYECTORIA
# ==========================================================

rad_heading = np.radians(
    90 - heading
)


def obtener_posicion_futura(
    future_h
):

    dist_nm = (
        forward_speed
        *
        future_h
    )

    dist_deg = (
        dist_nm
        /
        60.0
    )

    future_lon = (
        lon
        +
        dist_deg
        *
        np.cos(
            rad_heading
        )
    )

    future_lat = (
        lat
        +
        dist_deg
        *
        np.sin(
            rad_heading
        )
    )

    return (
        future_lat,
        future_lon
    )


forecast_hours = [
    0,
    12,
    24,
    36,
    48,
    72
]

nhc_radii_deg = [
    0.0,
    0.45,
    0.75,
    1.10,
    1.45,
    2.10
]

track_lons = []
track_lats = []
circles = []

for h, r in zip(
    forecast_hours,
    nhc_radii_deg
):

    future_lat, future_lon = (
        obtener_posicion_futura(
            h
        )
    )

    track_lons.append(
        future_lon
    )

    track_lats.append(
        future_lat
    )

    pt = Point(
        future_lon,
        future_lat
    )

    circles.append(
        pt.buffer(
            max(
                r,
                0.2
            )
        )
    )


cone_geom = unary_union(
    circles
).convex_hull


# ==========================================================
# MAPA PRINCIPAL
# ==========================================================

m = folium.Map(
    location=[
        lat,
        lon
    ],
    zoom_start=5,
    tiles="OpenStreetMap"
)

folium.GeoJson(
    mapping(
        cone_geom
    ),
    style_function=lambda x: {
        "fillColor": "white",
        "color": "red",
        "weight": 2,
        "fillOpacity": 0.35
    }
).add_to(m)

wind34 = create_wind_field(
    lon,
    lat,
    [
        r34_ne,
        r34_se,
        r34_sw,
        r34_nw
    ]
)

wind50 = create_wind_field(
    lon,
    lat,
    [
        r50_ne,
        r50_se,
        r50_sw,
        r50_nw
    ]
)

wind64 = create_wind_field(
    lon,
    lat,
    [
        r64_ne,
        r64_se,
        r64_sw,
        r64_nw
    ]
)

folium.GeoJson(
    mapping(
        wind34
    ),
    style_function=lambda x: {
        "color": "green",
        "weight": 2,
        "fillOpacity": 0
    }
).add_to(m)

folium.GeoJson(
    mapping(
        wind50
    ),
    style_function=lambda x: {
        "color": "orange",
        "weight": 2,
        "fillOpacity": 0
    }
).add_to(m)

folium.GeoJson(
    mapping(
        wind64
    ),
    style_function=lambda x: {
        "color": "red",
        "weight": 2,
        "fillOpacity": 0
    }
).add_to(m)

folium.PolyLine(
    locations=list(
        zip(
            track_lats,
            track_lons
        )
    ),
    color="black",
    weight=2,
    dash_array="8, 8"
).add_to(m)

for h, tx, ty in zip(
    forecast_hours,
    track_lons,
    track_lats
):

    folium.CircleMarker(
        location=[
            ty,
            tx
        ],
        radius=5,
        color="black",
        fill=True,
        fill_opacity=1,
        popup=(
            f"Pronóstico: +{h} horas"
        )
    ).add_to(m)

folium.CircleMarker(
    location=[
        lat,
        lon
    ],
    radius=8,
    color="red",
    fill=True,
    fill_color="red",
    fill_opacity=1,
    popup=(
        f"{name} — "
        f"{wind_speed} kt"
    )
).add_to(m)

m.fit_bounds([
    [
        min(track_lats) - 6,
        min(track_lons) - 6
    ],
    [
        max(track_lats) + 6,
        max(track_lons) + 6
    ]
])


col1, col2 = st.columns(
    [2, 1]
)


with col1:

    map_data = st_folium(
        m,
        width=None,
        height=600,
        key="mapa_principal"
    )

    if (
        map_data
        and
        map_data.get(
            "last_clicked"
        )
    ):

        clicked_lat = (
            map_data[
                "last_clicked"
            ]["lat"]
        )

        clicked_lon = (
            map_data[
                "last_clicked"
            ]["lng"]
        )

        st.session_state[
            "punto_seleccionado"
        ] = (
            clicked_lat,
            clicked_lon
        )

    punto_seleccionado = (
        st.session_state.get(
            "punto_seleccionado"
        )
    )

    if punto_seleccionado is not None:

        clicked_lat = (
            punto_seleccionado[0]
        )

        clicked_lon = (
            punto_seleccionado[1]
        )

        estimated_wind, distance_nm, quadrant = (
            calcular_viento_en_punto(
                clicked_lat,
                clicked_lon,
                lat,
                lon,
                wind_speed,
                r34_ne,
                r34_se,
                r34_sw,
                r34_nw,
                r50_ne,
                r50_se,
                r50_sw,
                r50_nw,
                r64_ne,
                r64_se,
                r64_sw,
                r64_nw
            )
        )

        estimated_category = (
            get_category(
                estimated_wind
            )
        )

        estimated_mph = (
            estimated_wind
            *
            1.15078
        )

        angle = np.degrees(
            np.arctan2(
                (
                    clicked_lon
                    -
                    lon
                )
                *
                np.cos(
                    np.radians(
                        lat
                    )
                ),
                clicked_lat
                -
                lat
            )
        )

        if angle < 0:

            angle += 360

        st.info(
            f"""
📍 **Punto seleccionado**
**Latitud:** {clicked_lat:.4f}°
**Longitud:** {clicked_lon:.4f}°
**Distancia al centro:** {distance_nm:.1f} NM
({distance_nm * 1.15078:.1f} millas)
**Dirección desde el centro:** {angle:.0f}°
**Cuadrante:** {quadrant}
"""
        )

        st.success(
            f"""
💨 **VIENTO ESTIMADO ACTUAL**
### {estimated_mph:.0f} mph
**Clasificación:** {estimated_category}
*Estimación académica basada en la distancia al centro y los Wind Radii definidos.*
"""
        )

        # ==================================================
        # EVOLUCIÓN 72 HORAS
        # ==================================================

        progression_hours = list(
            range(
                0,
                73,
                1
            )
        )

        progression_wind_kt = []
        progression_wind_mph = []
        progression_distance = []

        for future_h in progression_hours:

            future_lat, future_lon = (
                obtener_posicion_futura(
                    future_h
                )
            )

            future_wind, future_distance, future_quadrant = (
                calcular_viento_en_punto(
                    clicked_lat,
                    clicked_lon,
                    future_lat,
                    future_lon,
                    wind_speed,
                    r34_ne,
                    r34_se,
                    r34_sw,
                    r34_nw,
                    r50_ne,
                    r50_se,
                    r50_sw,
                    r50_nw,
                    r64_ne,
                    r64_se,
                    r64_sw,
                    r64_nw
                )
            )

            progression_wind_kt.append(
                future_wind
            )

            progression_wind_mph.append(
                future_wind
                *
                1.15078
            )

            progression_distance.append(
                future_distance
            )

        max_wind_kt = max(
            progression_wind_kt
        )

        max_wind_mph = (
            max_wind_kt
            *
            1.15078
        )

        max_index = (
            progression_wind_kt.index(
                max_wind_kt
            )
        )

        max_hour = (
            progression_hours[
                max_index
            ]
        )

        st.subheader(
            "📈 Evolución del viento"
        )

        st.write(
            "El punto permanece fijo mientras el centro "
            "del ciclón sigue la trayectoria definida."
        )

        fig, ax = plt.subplots(
            figsize=(9, 4.5)
        )

        ax.plot(
            progression_hours,
            progression_wind_mph,
            linewidth=2
        )

        ax.axhline(
            34 * 1.15078,
            linestyle="--",
            linewidth=1
        )

        ax.axhline(
            50 * 1.15078,
            linestyle="--",
            linewidth=1
        )

        ax.axhline(
            64 * 1.15078,
            linestyle="--",
            linewidth=1
        )

        ax.axvline(
            max_hour,
            linestyle=":",
            linewidth=1
        )

        ax.set_xlabel(
            "Horas desde la posición inicial"
        )

        ax.set_ylabel(
            "Viento sostenido (mph)"
        )

        ax.set_title(
            "Evolución del viento en el punto seleccionado"
        )

        ax.grid(
            True,
            alpha=0.3
        )

        st.pyplot(
            fig,
            use_container_width=True
        )

        st.metric(
            "💨 Viento máximo esperado",
            f"{max_wind_mph:.0f} mph",
            f"en +{max_hour} horas"
        )

        def encontrar_periodo(
            horas,
            vientos,
            umbral
        ):

            horas_dentro = []

            for h, viento in zip(
                horas,
                vientos
            ):

                if viento >= umbral:

                    horas_dentro.append(
                        h
                    )

            if not horas_dentro:

                return None, None

            return (
                min(horas_dentro),
                max(horas_dentro)
            )

        entrada34, salida34 = encontrar_periodo(
            progression_hours,
            progression_wind_kt,
            34
        )

        entrada50, salida50 = encontrar_periodo(
            progression_hours,
            progression_wind_kt,
            50
        )

        entrada64, salida64 = encontrar_periodo(
            progression_hours,
            progression_wind_kt,
            64
        )

        st.subheader(
            "🌀 Periodos de viento"
        )

        periodos = {
            "34 kt — Tormenta Tropical": (
                entrada34,
                salida34
            ),
            "50 kt": (
                entrada50,
                salida50
            ),
            "64 kt — Huracán": (
                entrada64,
                salida64
            )
        }

        for nombre_umbral, periodo in periodos.items():

            entrada, salida = periodo

            if entrada is not None:

                st.write(
                    f"**{nombre_umbral}:** "
                    f"entrada +{entrada} h → "
                    f"salida +{salida} h"
                )

            else:

                st.write(
                    f"**{nombre_umbral}:** "
                    "No alcanza este umbral."
                )

        # ==================================================
        # SIMULACIÓN DE 24 HORAS
        # ==================================================

        st.markdown("---")

        st.subheader(
            "🎬 Simulación de las próximas 24 horas"
        )

        st.write(
            "Usa el botón ▶️ dentro del mapa para iniciar "
            "la simulación. El punto azul permanece fijo."
        )

        punto_fijo_lat = clicked_lat
        punto_fijo_lon = clicked_lon

        animation_frames = []

        for future_h in range(
            0,
            25
        ):

            future_lat, future_lon = (
                obtener_posicion_futura(
                    future_h
                )
            )

            future_wind, future_distance, future_quadrant = (
                calcular_viento_en_punto(
                    punto_fijo_lat,
                    punto_fijo_lon,
                    future_lat,
                    future_lon,
                    wind_speed,

                    r34_ne,
                    r34_se,
                    r34_sw,
                    r34_nw,

                    r50_ne,
                    r50_se,
                    r50_sw,
                    r50_nw,

                    r64_ne,
                    r64_se,
                    r64_sw,
                    r64_nw
                )
            )

            future_category = (
                get_category(
                    future_wind
                )
            )

            future_wind_mph = (
                future_wind
                *
                1.15078
            )

            wind34_future = create_wind_field(
                future_lon,
                future_lat,
                [
                    r34_ne,
                    r34_se,
                    r34_sw,
                    r34_nw
                ]
            )

            wind50_future = create_wind_field(
                future_lon,
                future_lat,
                [
                    r50_ne,
                    r50_se,
                    r50_sw,
                    r50_nw
                ]
            )

            wind64_future = create_wind_field(
                future_lon,
                future_lat,
                [
                    r64_ne,
                    r64_se,
                    r64_sw,
                    r64_nw
                ]
            )

            animation_frames.append(
                {
                    "hour": future_h,
                    "lat": future_lat,
                    "lon": future_lon,
                    "wind_mph": future_wind_mph,
                    "wind_kt": future_wind,
                    "distance": future_distance,
                    "category": future_category,
                    "quadrant": future_quadrant,
                    "wind34": mapping(
                        wind34_future
                    ),
                    "wind50": mapping(
                        wind50_future
                    ),
                    "wind64": mapping(
                        wind64_future
                    )
                }
            )

        # ==================================================
        # MAPA DE ANIMACIÓN
        # ==================================================

        mapa_animacion = folium.Map(
            location=[
                lat,
                lon
            ],
            zoom_start=5,
            tiles="OpenStreetMap"
        )

        folium.GeoJson(
            mapping(
                cone_geom
            ),
            style_function=lambda x: {
                "fillColor": "white",
                "color": "red",
                "weight": 2,
                "fillOpacity": 0.20
            }
        ).add_to(
            mapa_animacion
        )

        folium.PolyLine(
            locations=list(
                zip(
                    track_lats,
                    track_lons
                )
            ),
            color="black",
            weight=2,
            dash_array="8, 8"
        ).add_to(
            mapa_animacion
        )

        for h, tx, ty in zip(
            forecast_hours,
            track_lons,
            track_lats
        ):

            folium.CircleMarker(
                location=[
                    ty,
                    tx
                ],
                radius=4,
                color="black",
                fill=True,
                fill_opacity=1,
                popup=(
                    f"Pronóstico: +{h} horas"
                )
            ).add_to(
                mapa_animacion
            )

        # ==================================================
        # CAMPOS DE VIENTO
        # ==================================================

        wind34_layer = folium.Polygon(
            locations=[
                [y, x]
                for x, y in wind34.exterior.coords
            ],
            color="green",
            weight=3,
            fill=False
        ).add_to(
            mapa_animacion
        )

        wind50_layer = folium.Polygon(
            locations=[
                [y, x]
                for x, y in wind50.exterior.coords
            ],
            color="orange",
            weight=3,
            fill=False
        ).add_to(
            mapa_animacion
        )

        wind64_layer = folium.Polygon(
            locations=[
                [y, x]
                for x, y in wind64.exterior.coords
            ],
            color="red",
            weight=3,
            fill=False
        ).add_to(
            mapa_animacion
        )

        # ==================================================
        # CENTRO MÓVIL
        # ==================================================

        center_marker = folium.CircleMarker(
            location=[
                lat,
                lon
            ],
            radius=9,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=1,
            popup=(
                f"{name} — "
                f"{wind_speed} kt"
            )
        ).add_to(
            mapa_animacion
        )

        # ==================================================
        # PUNTO AZUL FIJO
        # ==================================================

        folium.CircleMarker(
            location=[
                punto_fijo_lat,
                punto_fijo_lon
            ],
            radius=9,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=1,
            weight=3,
            popup="📍 Punto seleccionado"
        ).add_to(
            mapa_animacion
        )

        mapa_animacion.fit_bounds([
            [
                min(track_lats) - 6,
                min(track_lons) - 6
            ],
            [
                max(track_lats) + 6,
                max(track_lons) + 6
            ]
        ])

        frames_json = json.dumps(
            animation_frames
        )

        map_name = (
            mapa_animacion.get_name()
        )

        wind34_name = (
            wind34_layer.get_name()
        )

        wind50_name = (
            wind50_layer.get_name()
        )

        wind64_name = (
            wind64_layer.get_name()
        )

        center_marker_name = (
            center_marker.get_name()
        )

        # ==================================================
        # JAVASCRIPT
        # BOTÓN PLAY DENTRO DEL MAPA
        # ==================================================

        animation_script = """
(function() {

    var mapAnimation = __MAP_NAME__;

    var wind34Layer = __WIND34_NAME__;
    var wind50Layer = __WIND50_NAME__;
    var wind64Layer = __WIND64_NAME__;

    var centerMarker = __CENTER_MARKER_NAME__;

    var frames = __FRAMES_JSON__;

    var frameIndex = 0;
    var animationTimer = null;
    var animationStarted = false;

    function convertirCoordenadas(
        coordinates
    ) {

        return coordinates.map(
            function(point) {

                return [
                    point[1],
                    point[0]
                ];

            }
        );

    }


    function renderFrame(index) {

        var frame =
            frames[index];

        if (!frame) {
            return;
        }

        // ----------------------------------------------
        // MOVER CENTRO
        // ----------------------------------------------

        centerMarker.setLatLng([
            frame.lat,
            frame.lon
        ]);

        // ----------------------------------------------
        // MOVER CAMPO 34 KT
        // ----------------------------------------------

        wind34Layer.setLatLngs(
            convertirCoordenadas(
                frame.wind34.geometry.coordinates[0]
            )
        );

        // ----------------------------------------------
        // MOVER CAMPO 50 KT
        // ----------------------------------------------

        wind50Layer.setLatLngs(
            convertirCoordenadas(
                frame.wind50.geometry.coordinates[0]
            )
        );

        // ----------------------------------------------
        // MOVER CAMPO 64 KT
        // ----------------------------------------------

        wind64Layer.setLatLngs(
            convertirCoordenadas(
                frame.wind64.geometry.coordinates[0]
            )
        );

        // ----------------------------------------------
        // ACTUALIZAR INFORMACIÓN
        // ----------------------------------------------

        var info =
            document.getElementById(
                "animation-info"
            );

        if (info) {

            info.innerHTML =
                "<b>🎬 Simulación 24 horas</b><br>" +
                "⏱️ <b>+" +
                frame.hour +
                " horas</b><br>" +
                "📍 Centro: " +
                frame.lat.toFixed(4) +
                "°, " +
                Math.abs(
                    frame.lon
                ).toFixed(4) +
                "°W<br>" +
                "📏 Distancia: " +
                frame.distance.toFixed(1) +
                " NM<br>" +
                "💨 Viento: <b>" +
                frame.wind_mph.toFixed(0) +
                " mph</b><br>" +
                "🌀 Clasificación: " +
                frame.category +
                "<br>" +
                "🧭 Cuadrante: " +
                frame.quadrant;

        }

    }


    // ==================================================
    // CREAR CONTROLES CUANDO EL MAPA ESTÉ LISTO
    // ==================================================

    function iniciarControles() {

        if (
            animationStarted
        ) {
            return;
        }

        animationStarted = true;


        // ==================================================
        // PANEL DE INFORMACIÓN
        // ==================================================

        var infoControl = L.control({
            position: "topright"
        });

        infoControl.onAdd = function(map) {

            var div = L.DomUtil.create(
                "div",
                "animation-info-control"
            );

            div.id =
                "animation-info";

            div.style.backgroundColor =
                "white";

            div.style.padding =
                "12px 15px";

            div.style.borderRadius =
                "8px";

            div.style.boxShadow =
                "0 2px 8px rgba(0,0,0,0.30)";

            div.style.fontFamily =
                "Arial, sans-serif";

            div.style.fontSize =
                "14px";

            div.style.lineHeight =
                "1.5";

            div.style.minWidth =
                "230px";

            div.innerHTML =
                "<b>🎬 Simulación 24 horas</b><br>" +
                "<span>Listo para comenzar</span>";

            L.DomEvent.disableClickPropagation(
                div
            );

            return div;

        };

        infoControl.addTo(
            mapAnimation
        );


        // ==================================================
        // BOTÓN PLAY
        // ==================================================

        var playControl = L.control({
            position: "topleft"
        });

        playControl.onAdd = function(map) {

            var container = L.DomUtil.create(
                "div"
            );

            container.style.marginTop =
                "10px";

            container.style.marginLeft =
                "10px";

            container.style.background =
                "transparent";

            var button =
                document.createElement(
                    "button"
                );

            button.type =
                "button";

            button.id =
                "play-24h-button";

            button.innerHTML =
                "▶️ Play 24h";

            button.title =
                "Simular próximas 24 horas";

            button.style.display =
                "block";

            button.style.visibility =
                "visible";

            button.style.opacity =
                "1";

            button.style.backgroundColor =
                "white";

            button.style.color =
                "black";

            button.style.border =
                "2px solid #555";

            button.style.borderRadius =
                "6px";

            button.style.padding =
                "8px 14px";

            button.style.fontSize =
                "14px";

            button.style.fontWeight =
                "bold";

            button.style.cursor =
                "pointer";

            button.style.whiteSpace =
                "nowrap";

            button.style.minWidth =
                "110px";

            button.style.height =
                "40px";

            button.style.boxShadow =
                "0 2px 6px rgba(0,0,0,0.30)";

            container.appendChild(
                button
            );

            L.DomEvent.disableClickPropagation(
                container
            );

            L.DomEvent.on(
                button,
                "click",
                function() {

                    // ----------------------------------
                    // PAUSAR
                    // ----------------------------------

                    if (
                        animationTimer !== null
                    ) {

                        clearInterval(
                            animationTimer
                        );

                        animationTimer =
                            null;

                        button.innerHTML =
                            "▶️ Play 24h";

                        return;

                    }


                    // ----------------------------------
                    // REINICIAR
                    // ----------------------------------

                    if (
                        frameIndex >=
                        frames.length - 1
                    ) {

                        frameIndex = 0;

                        renderFrame(
                            frameIndex
                        );

                    }


                    // ----------------------------------
                    // REPRODUCIR
                    // ----------------------------------

                    button.innerHTML =
                        "⏸️ Pausar";

                    animationTimer =
                        setInterval(
                            function() {

                                frameIndex += 1;

                                if (
                                    frameIndex >=
                                    frames.length
                                ) {

                                    clearInterval(
                                        animationTimer
                                    );

                                    animationTimer =
                                        null;

                                    frameIndex =
                                        frames.length - 1;

                                    button.innerHTML =
                                        "🔄 Reiniciar";

                                    return;

                                }

                                renderFrame(
                                    frameIndex
                                );

                            },
                            500
                        );

                }
            );

            return container;

        };


        playControl.addTo(
            mapAnimation
        );


        // ==================================================
        // FRAME INICIAL
        // ==================================================

        renderFrame(0);

    }


    // ==================================================
    // ESPERAR A QUE LEAFLET ESTÉ LISTO
    // ==================================================

    if (
        mapAnimation &&
        mapAnimation.whenReady
    ) {

        mapAnimation.whenReady(
            function() {

                iniciarControles();

            }
        );

    } else {

        setTimeout(
            function() {

                iniciarControles();

            },
            500
        );

    }

})();
"""

        animation_script = (
            animation_script
            .replace(
                "__MAP_NAME__",
                map_name
            )
            .replace(
                "__WIND34_NAME__",
                wind34_name
            )
            .replace(
                "__WIND50_NAME__",
                wind50_name
            )
            .replace(
                "__WIND64_NAME__",
                wind64_name
            )
            .replace(
                "__CENTER_MARKER_NAME__",
                center_marker_name
            )
            .replace(
                "__FRAMES_JSON__",
                frames_json
            )
        )

        mapa_animacion.get_root().script.add_child(
            Element(
                animation_script
            )
        )

        st.caption(
            "Cada 0.5 segundos representa 1 hora de simulación. "
            "El punto azul permanece fijo."
        )

        st_folium(
            mapa_animacion,
            width=None,
            height=600,
            key="mapa_animacion_24h"
        )


# ==========================================================
# COLUMNA DERECHA
# ==========================================================

with col2:

    st.subheader(
        "Boletín de Advertencia"
    )

    st.markdown(
        f"""
**SISTEMA:** {name}  
**CLASIFICACIÓN:** {category_str}  
**UBICACIÓN ACTUAL:** {lat:.1f}°N {abs(lon):.1f}°W  
**VIENTOS MÁXIMOS:** {wind_speed} nudos
(~{int(wind_speed * 1.852)} km/h)  
**MOVIMIENTO ACTUAL:** Rumbo {heading}°
a {forward_speed} kt
"""
    )

    st.info(
        "Nota didáctica: El cono representa el área "
        "probable del centro del ciclón en las próximas "
        "72 horas. Los efectos del viento y lluvia se "
        "extienden significativamente fuera de esta zona."
    )
