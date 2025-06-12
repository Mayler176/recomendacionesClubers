import streamlit as st
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from math import radians, sin, cos, sqrt, atan2
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium

# --- Funciones auxiliares ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def recomendar(cliente_id, n=10):
    if cliente_id not in cli_idx_map:
        raise ValueError("Cliente no encontrado.")
    idx = cli_idx_map[cliente_id]
    sims = cosine_similarity(cli_vecs[idx], rest_vecs).flatten()
    resultados = desc_rest[['NumeroProveedor']].copy()
    resultados['similarity'] = sims
    resultados = resultados.merge(
        socios[['NumeroProveedor', 'CategoryId', 'NombreRestaurante', 'latitud', 'longitud']],
        on='NumeroProveedor'
    )
    resultados = resultados.sort_values(by='similarity', ascending=False)
    resultados = resultados.groupby('CategoryId', group_keys=False).head(2)
    return resultados.head(n)

@st.cache_resource
def cargar_modelo():
    with open('modelo_recomendador.pkl', 'rb') as f:
        return pickle.load(f)

# --- Función principal que llama app.py ---
def run():

    try:
        raise Exception("Debug start")
    except Exception as e:
        st.info("ModeloPlatillos iniciado correctamente.")

    st.title("Recomendador de Restaurantes")

    # Carga del modelo (cacheado)

    # modelo = cargar_modelo()
    tfidf_vec = None
    rest_vecs = None
    cli_vecs = None
    cli_idx_map = {24: 0}  # Simula que el cliente existe
    desc_rest = pd.DataFrame({
        'NumeroProveedor': [1,2,3,4,5],
        'NombreRestaurante': ['A','B','C','D','E'],
        'latitud': [25.65]*5,
        'longitud': [-100.29]*5,
        'CategoryId': [1,2,3,4,5]
    })
    socios = desc_rest.copy()
    perfil_cliente = pd.DataFrame()


    #modelo = cargar_modelo()


    # Interfaz
    cliente_id = st.number_input("Ingresa tu ID de cliente:", min_value=0, step=1)

    if st.button("Obtener recomendaciones"):
        try:
            recs = recomendar(cliente_id, n=10)

            # Ubicación simulada del usuario
            user_lat, user_lon = 25.651435, -100.290686
            st.markdown(f"**Ubicación del usuario:** {user_lat:.5f}, {user_lon:.5f}")

            recs['distance_km'] = recs.apply(
                lambda row: haversine(user_lat, user_lon, row['latitud'], row['longitud']),
                axis=1
            )

            recs_ordenadas = recs.sort_values(by=['distance_km', 'similarity'], ascending=[True, True])
            top5 = recs_ordenadas.head(5)

            st.subheader("Top 5 Recomendaciones")
            st.dataframe(top5[['NombreRestaurante', 'CategoryId', 'similarity', 'distance_km']])

            # Mapa
            geometry = [Point(xy) for xy in zip(top5['longitud'], top5['latitud'])]
            gdf_recs = gpd.GeoDataFrame(top5, geometry=geometry, crs="EPSG:4326")

            user_geom = Point(user_lon, user_lat)
            gdf_user = gpd.GeoDataFrame(
                pd.DataFrame({'Nombre': ['Usuario']}),
                geometry=[user_geom],
                crs="EPSG:4326"
            )

            m = folium.Map(location=[user_lat, user_lon], zoom_start=13)

            for _, row in gdf_recs.iterrows():
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=row['NombreRestaurante'],
                    icon=folium.Icon(color='blue', icon='cutlery', prefix='fa')
                ).add_to(m)

            folium.Marker(
                location=[user_lat, user_lon],
                popup='Usuario',
                icon=folium.Icon(color='red', icon='star')
            ).add_to(m)

            st.subheader("Mapa de Recomendaciones")
            st_folium(m, width=700, height=500)

        except ValueError as e:
            st.error(str(e))
