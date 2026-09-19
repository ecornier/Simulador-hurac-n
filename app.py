import streamlit as st
from best_tracks import descargar_hurdat, buscar_ciclon
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import folium
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from streamlit_folium import st_folium

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from streamlit_folium import st_folium
st.set_page_config(page_title="Simulador de Huracanes NHC", layout="wide")

st.title("🌀 Simulador Académico de Huracanes (Estilo NHC)")

st.sidebar.header("Parámetros del Ciclón")
modo = st.sidebar.radio(
    "Modo de simulación",
    ["Huracán hipotético", "Ciclón tropical histórico"]
)
name = st.sidebar.text_input("Nombre de la Tormenta", value="ALBERTO")
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
    datos_ciclon = buscar_ciclon(datos_hurdat, ciclón.split(" (")[0])

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
                f"{fecha} {hora} UTC — {lat_hurdat}, {lon_hurdat}"
            )

    posicion = st.sidebar.selectbox(
        "Posición histórica",
        opciones_posicion
    )
    if modo == "Ciclón tropical histórico":
    partes_posicion = posicion.split("—")
    coordenadas = partes_posicion[1].strip().split(",")

    lat = float(coordenadas[0].strip().replace("N", ""))
    lon = float(coordenadas[1].strip().replace("W", "-"))
lat = lat = st.sidebar.number_input(
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
wind_speed = st.sidebar.slider("Vientos Sostenidos (nudos)", min_value=30, max_value=165, value=75, step=5)
heading = st.sidebar.slider("Rumbo (°)", min_value=0, max_value=360, value=290, step=5)
forward_speed = st.sidebar.slider("Velocidad de Avance (kt)", min_value=5, max_value=25, value=12, step=1)


st.sidebar.markdown("---")
st.sidebar.header("Wind Radii")

st.sidebar.markdown("---")
st.sidebar.header("Wind Radii")

st.sidebar.subheader("34 kt — Tormenta Tropical")
st.sidebar.header("Wind Radii")



r34_ne = st.sidebar.number_input("34 kt — NE", min_value=0.0, max_value=500.0, value=120.0, step=5.0)
r34_se = st.sidebar.number_input("34 kt — SE", min_value=0.0, max_value=500.0, value=100.0, step=5.0)
r34_sw = st.sidebar.number_input("34 kt — SW", min_value=0.0, max_value=500.0, value=80.0, step=5.0)
r34_nw = st.sidebar.number_input("34 kt — NW", min_value=0.0, max_value=500.0, value=100.0, step=5.0)

st.sidebar.subheader("50 kt")

r50_ne = st.sidebar.number_input("50 kt — NE", min_value=0.0, max_value=400.0, value=70.0, step=5.0)
r50_se = st.sidebar.number_input("50 kt — SE", min_value=0.0, max_value=400.0, value=60.0, step=5.0)
r50_sw = st.sidebar.number_input("50 kt — SW", min_value=0.0, max_value=400.0, value=45.0, step=5.0)
r50_nw = st.sidebar.number_input("50 kt — NW", min_value=0.0, max_value=400.0, value=60.0, step=5.0)

st.sidebar.subheader("64 kt — Huracán")

r64_ne = st.sidebar.number_input("64 kt — NE", min_value=0.0, max_value=300.0, value=35.0, step=5.0)
r64_se = st.sidebar.number_input("64 kt — SE", min_value=0.0, max_value=300.0, value=30.0, step=5.0)
r64_sw = st.sidebar.number_input("64 kt — SW", min_value=0.0, max_value=300.0, value=20.0, step=5.0)
r64_nw = st.sidebar.number_input("64 kt — NW", min_value=0.0, max_value=300.0, value=30.0, step=5.0)
    
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

category_str = get_category(wind_speed)
def create_wind_field(center_lon, center_lat, radii):
    """
    Crea un campo de viento redondeado utilizando
    cuatro radios: NE, SE, SW y NW.
    """

    # Ángulos correspondientes al centro de cada cuadrante
    quadrant_angles = np.array([45, 135, 225, 315], dtype=float)

    # Radios: NE, SE, SW, NW
    quadrant_radii = np.array(radii, dtype=float)

    # 360 puntos para crear una curva muy suave
    angles = np.linspace(0, 360, 361)

    interpolated_radii = []

    for angle in angles[:-1]:

        # Determinar entre qué dos cuadrantes estamos
        if angle >= 315 or angle < 45:
            r1 = quadrant_radii[3]  # NW
            r2 = quadrant_radii[0]  # NE

            if angle >= 315:
                t = (angle - 315) / 90
            else:
                t = (angle + 45) / 90

        elif angle < 135:
            r1 = quadrant_radii[0]  # NE
            r2 = quadrant_radii[1]  # SE
            t = (angle - 45) / 90

        elif angle < 225:
            r1 = quadrant_radii[1]  # SE
            r2 = quadrant_radii[2]  # SW
            t = (angle - 135) / 90

        else:
            r1 = quadrant_radii[2]  # SW
            r2 = quadrant_radii[3]  # NW
            t = (angle - 225) / 90

        # Mantener t dentro de 0–1
        t = np.clip(t, 0, 1)

        # Interpolación suave
        smooth_t = (1 - np.cos(np.pi * t)) / 2

        radius = (
            r1 * (1 - smooth_t)
            + r2 * smooth_t
        )

        interpolated_radii.append(radius)

    interpolated_radii = np.array(interpolated_radii)

    # --------------------------------------------------
    # Convertir millas náuticas a grados
    # --------------------------------------------------

    lat_deg = interpolated_radii / 60.0

    lon_deg = interpolated_radii / (
        60.0 * np.cos(np.radians(center_lat))
    )

    # Convertir de ángulo meteorológico
    # a coordenadas X/Y
    math_angles = np.radians(
        90 - angles[:-1]
    )

    x = center_lon + lon_deg * np.cos(math_angles)
    y = center_lat + lat_deg * np.sin(math_angles)

    coordinates = np.column_stack((x, y))

    return Polygon(coordinates)
forecast_hours = [0, 12, 24, 36, 48, 72]
nhc_radii_deg = [0.0, 0.45, 0.75, 1.10, 1.45, 2.10]

track_lons = []
track_lats = []
circles = []

rad_heading = np.radians(90 - heading)
for h, r in zip(forecast_hours, nhc_radii_deg):
    dist_nm = forward_speed * h
    dist_deg = dist_nm / 60.0
    
    fx = lon + dist_deg * np.cos(rad_heading)
    fy = lat + dist_deg * np.sin(rad_heading)
    
    track_lons.append(fx)
    track_lats.append(fy)
    
    pt = Point(fx, fy)
    circles.append(pt.buffer(max(r, 0.2)))

cone_geom = unary_union(circles).convex_hull
wind34 = create_wind_field(
    lon,
    lat,
    [r34_ne, r34_se, r34_sw, r34_nw]
)

wind50 = create_wind_field(
    lon,
    lat,
    [r50_ne, r50_se, r50_sw, r50_nw]
)

wind64 = create_wind_field(
    lon,
    lat,
    [r64_ne, r64_se, r64_sw, r64_nw]
)



# MAPA INTERACTIVO

from shapely.geometry import mapping
# MAPA INTERACTIVO

from shapely.geometry import mapping

m = folium.Map(
    location=[lat, lon],
    zoom_start=5,
    tiles="OpenStreetMap"
)

# Cono de pronóstico
folium.GeoJson(
    mapping(cone_geom),
    style_function=lambda x: {
        "fillColor": "white",
        "color": "red",
        "weight": 2,
        "fillOpacity": 0.35
    }
).add_to(m)

# Radio 34 kt
folium.GeoJson(
    mapping(wind34),
    style_function=lambda x: {
        "color": "green",
        "weight": 2,
        "fillOpacity": 0
    }
).add_to(m)

# Radio 50 kt
folium.GeoJson(
    mapping(wind50),
    style_function=lambda x: {
        "color": "orange",
        "weight": 2,
        "fillOpacity": 0
    }
).add_to(m)

# Radio 64 kt
folium.GeoJson(
    mapping(wind64),
    style_function=lambda x: {
        "color": "red",
        "weight": 2,
        "fillOpacity": 0
    }
).add_to(m)

# Trayectoria
folium.PolyLine(
    locations=list(zip(track_lats, track_lons)),
    color="black",
    weight=2,
    dash_array="8, 8"
).add_to(m)

# Puntos de pronóstico
for h, tx, ty in zip(forecast_hours, track_lons, track_lats):
    folium.CircleMarker(
        location=[ty, tx],
        radius=5,
        color="black",
        fill=True,
        fill_opacity=1,
        popup=f"Pronóstico: +{h} horas"
    ).add_to(m)

# Centro actual
folium.CircleMarker(
    location=[lat, lon],
    radius=8,
    color="red",
    fill=True,
    fill_color="red",
    fill_opacity=1,
    popup=f"{name} — {wind_speed} kt"
).add_to(m)

# Ajustar vista
m.fit_bounds([
    [min(track_lats) - 6, min(track_lons) - 6],
    [max(track_lats) + 6, max(track_lons) + 6]
])

# Crear las dos columnas
col1, col2 = st.columns([2, 1])

with col1:
    map_data = st_folium(
        m,
        width=None,
        height=600
    )

    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]

        st.info(
            f"📍 Punto seleccionado: "
            f"{clicked_lat:.4f}°N, "
            f"{abs(clicked_lon):.4f}°W"
        )

with col2:
    st.subheader("Boletín de Advertencia")
    st.markdown(f"""
    **SISTEMA:** {name}  
    **CLASIFICACIÓN:** {category_str}  
    **UBICACIÓN ACTUAL:** {lat:.1f}°N {abs(lon):.1f}°W  
    **VIENTOS MÁXIMOS:** {wind_speed} nudos (~{int(wind_speed * 1.852)} km/h)  
    **MOVIMIENTO ACTUAL:** Rumbo {heading}° a {forward_speed} kt  
    """)
    
    st.info("Nota didáctica: El cono representa el área probable del centro del ciclón en las próximas 72 horas. Los efectos del viento y lluvia se extienden significativamente fuera de esta zona.")
