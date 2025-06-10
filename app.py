import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_distances
from mpl_toolkits.mplot3d import Axes3D

from streamlit_elements import elements, mui, html
from streamlit_elements import nivo

# ----------- CARGA DE DATOS Y MODELO ----------- #
with open('svd_model.pkl', 'rb') as f:
    modelo = pickle.load(f)

X_rests_svd = modelo['X_rests_svd']
X_clients_svd = modelo['X_clients_svd']
df_final = modelo['df_final']
df_categorias_restaurantes_clubers = modelo['df_categorias_restaurantes_clubers']
df_rest_info = modelo['df_rest_info']

# ----------- FUNCIONES AUXILIARES ----------- #
def get_feature_columns():
    return [c for c in df_categorias_restaurantes_clubers.columns if c not in ('EstablishmentId', 'category')]

def get_client_preferences(client_id):
    idxs = df_final.index[df_final['NumeroSocioConsumidor'] == client_id].tolist()
    if not idxs:
        return None
    idx = idxs[0]
    feature_cols = get_feature_columns()
    preferencias = df_final.loc[idx, feature_cols]
    return preferencias[preferencias > 0].sort_values(ascending=False)

def plot_preference_pie_nivo(client_id):
    preferencias = get_client_preferences(client_id)
    if preferencias is None or preferencias.empty:
        st.warning("Este cliente no tiene preferencias registradas.")
        return

    pie_data = [{"id": k, "label": k, "value": v, "color": f"hsl({(i*37)%360}, 70%, 50%)"} for i, (k, v) in enumerate(preferencias.items())]

    with elements("nivo_pie_chart"):
        with mui.Box(sx={"height": 500}):
            nivo.Pie(
                data=pie_data,
                margin={"top": 100, "right": 100, "bottom": 100, "left": 100},
                innerRadius=0.5,
                padAngle=0.7,
                cornerRadius=3,
                activeOuterRadiusOffset=8,
                borderWidth=1,
                borderColor={"from": "color", "modifiers": [["darker", 0.8]]},
                arcLinkLabelsSkipAngle=10,
                arcLinkLabelsTextColor="grey",
                arcLinkLabelsThickness=2,
                arcLinkLabelsColor={"from": "color"},
                arcLabelsSkipAngle=10,
                arcLabelsTextColor={"from": "color", "modifiers": [["darker", 4]]},
                legends=[
                    {
                        "anchor": "bottom",
                        "direction": "row",
                        "translateY": 56,
                        "itemWidth": 100,
                        "itemHeight": 18,
                        "itemTextColor": "#999",
                        "symbolSize": 18,
                        "symbolShape": "circle",
                        "effects": [{"on": "hover", "style": {"itemTextColor": "#000"}}],
                    }
                ],
            )

def recommend_restaurants_for_client_SVD(client_id, n=5):
    idxs = df_final.index[df_final['NumeroSocioConsumidor'] == client_id].tolist()
    if not idxs:
        return None, f"Cliente {client_id} no encontrado.", None
    idx = idxs[0]
    client_vec_svd = X_clients_svd[idx].reshape(1, -1)
    dists = cosine_distances(client_vec_svd, X_rests_svd)[0]
    nearest = dists.argsort()[:n]

    recs = pd.DataFrame({
        'EstablishmentId': df_categorias_restaurantes_clubers.iloc[nearest]['EstablishmentId'].values,
        'distance': dists[nearest]
    })
    recs['similarity'] = 1 - recs['distance']
    recs = recs.merge(df_rest_info, on='EstablishmentId', how='left')

    top_cats = get_client_preferences(client_id).head(3).index.tolist()
    recs['Cliente_Gusta'] = ", ".join(top_cats)

    result = recs[['RestaurantName', 'distance', 'similarity', 'Latitude', 'Longitude', 'Cliente_Gusta']]

    # Gráfico 3D
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(projection='3d')
    ax.scatter(X_rests_svd[:, 0], X_rests_svd[:, 1], X_rests_svd[:, 2],
               marker='o', alpha=0.4, label='Restaurants')
    ax.scatter(X_rests_svd[nearest, 0], X_rests_svd[nearest, 1], X_rests_svd[nearest, 2],
               marker='X', s=100, c='red', label='Recommended')
    ax.scatter(client_vec_svd[0, 0], client_vec_svd[0, 1], client_vec_svd[0, 2],
               marker='^', s=150, c='green', label=f'Client {client_id}')
    ax.set_xlabel('SVD Comp1')
    ax.set_ylabel('SVD Comp2')
    ax.set_zlabel('SVD Comp3')
    ax.set_title(f'3D SVD: Cliente {client_id} & Recomendados')
    ax.legend(loc='best')
    plt.tight_layout()

    return result, None, fig

# ----------- INTERFAZ STREAMLIT ----------- #
st.set_page_config(page_title="Recomendador Clubers", layout="centered")
st.title("🍽️ Recomendador de Restaurantes - Clubers")

# Menú desplegable arriba
cliente_ids = df_final['NumeroSocioConsumidor'].sort_values().unique()
client_id = st.selectbox("Selecciona un cliente", cliente_ids)
num_recs = st.slider("Número de recomendaciones", 1, 10, value=5)

# Mostrar recomendaciones
resultados, error, fig3d = recommend_restaurants_for_client_SVD(client_id, n=num_recs)
if error:
    st.error(error)
else:
    st.success("¡Recomendaciones generadas exitosamente!")
    st.dataframe(resultados)

# ----------- INSIGHTS ----------- #
st.markdown("## 📊 Insights del Cliente")
st.markdown("#### Preferencias de categorías de comida (Pie Chart)")
plot_preference_pie_nivo(client_id)

st.markdown("#### Visualización 3D en espacio SVD")
if fig3d:
    st.pyplot(fig3d)
