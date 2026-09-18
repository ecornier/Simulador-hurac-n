import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import Point
from shapely.ops import unary_union

st.set_page_config(page_title="Simulador de Huracanes NHC", layout="wide")

st.title("🌀 Simulador Académico de Huracanes (Estilo NHC)")

st.sidebar.header("Parámetros del Ciclón")

name = st.sidebar.text_input("Nombre de la Tormenta", value="ALBERTO")
lat = st.sidebar.slider("Latitud Inicial (°N)", min_value=10.0, max_value=35.0, value=20.0, step=0.1)
lon = st.sidebar.slider("Longitud Inicial (°W)", min_value=-98.0, max_value=-40.0, value=-70.0, step=0.1)
wind_speed = st.sidebar.slider("Vientos Sostenidos (nudos)", min_value=30, max_value=165, value=75, step=5)
heading = st.sidebar.slider("Rumbo (°)", min_value=0, max_value=360, value=290, step=5)
forward_speed = st.sidebar.slider("Velocidad de Avance (kt)", min_value=5, max_value=25, value=12, step=1)
st.sidebar.markdown("---")
st.sidebar.header("Wind Radii")

st.sidebar.subheader("34 kt — Tormenta Tropical")

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

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

margin = 6.0
ax.set_extent([min(track_lons) - margin, max(track_lons) + margin, 
               min(track_lats) - margin, max(track_lats) + margin], 
              crs=ccrs.PlateCarree())

ax.add_feature(cfeature.LAND, facecolor="#e8e4d9")
ax.add_feature(cfeature.OCEAN, facecolor="#bfe2f7")
ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor="#555555")
ax.add_feature(cfeature.BORDERS, linestyle=":", edgecolor="#777777")
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, color="gray", alpha=0.3)

ax.add_geometries([cone_geom], crs=ccrs.PlateCarree(), facecolor="white", edgecolor="red", alpha=0.45, linewidth=1.2)
ax.plot(track_lons, track_lats, color="black", linestyle="--", linewidth=1.5, transform=ccrs.PlateCarree(), label="Pronóstico")
ax.scatter(track_lons, track_lats, color="black", s=30, zorder=5, transform=ccrs.PlateCarree())
ax.plot(lon, lat, marker="o", color="red", markersize=9, transform=ccrs.PlateCarree(), label="Centro Actual")

for h, tx, ty in zip(forecast_hours, track_lons, track_lats):
    ax.text(tx + 0.3, ty + 0.3, f"{h}h", transform=ccrs.PlateCarree(), fontsize=8, weight="bold")

ax.set_title(f"Centro Nacional de Huracanes (NHC) - Cono de Pronóstico\n{name} - Vientos: {wind_speed} kt ({category_str})", fontsize=11, weight="bold")
ax.legend(loc="lower left", fontsize=8)

col1, col2 = st.columns([2, 1])

with col1:
    st.pyplot(fig)

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
