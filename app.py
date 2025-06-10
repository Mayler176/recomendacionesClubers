import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_distances
from mpl_toolkits.mplot3d import Axes3D

# ----------- CARGA DE DATOS Y MODELO ----------- #
with open('svd_model.pkl', 'rb') as f:
    modelo = pickle.load(f)

X_rests_svd = modelo['X_rests_svd']
X_clients_svd = modelo['X_clients_svd']
df_final = modelo['df_final']
df_categorias_restaurantes_clubers = modelo['df_categorias_restaurantes_clubers']
df_rest_info = modelo['df_rest_info']

# ----------- FUNCIÓN PIE CHART ----------- #
def plot_preference_pie(client_id):
    idxs = df_final.index[df_final['NumeroSocioConsumidor'] == client_id].tolist()
    if not idxs:
        return None
    idx = idxs[0]

    feature_cols = [c for c in df_categorias_restaurantes_clubers.columns if c not in ('EstablishmentId', 'category')]
    preferencias = df_final.loc[idx, feature_cols]
    preferencias = preferencias[preferencias > 0]

    if preferencias.empty:
        return None

    fig, ax = plt.subplots()
    ax.pie(preferencias, labels=preferencias.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title(f"Preferencias del Cliente {client_id}")
    return fig

# ----------- FUNCIÓN DE RECOMENDACIÓN ----------- #
def recommend_restaurants_for_client_SVD(client_id, n=5, plot_3d=False):
    idxs = df_final.index[df_final['NumeroSocioConsumidor'] == client_id].tolist()
    if not idxs:
        return None, f"Cliente {client_id} no encontrado."
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

    feature_cols = [c for c in df_categorias_restaurantes_clubers.columns if c not in ('EstablishmentId', 'category')]
    top_cats_idx = df_final.loc[idx, feature_cols].sort_values(ascending=False).head(3)
    categorias_favoritas = ", ".join(top_cats_idx.index)
    recs['Cliente_Gusta'] = categorias_favoritas

    result = recs[['RestaurantName', 'distance', 'similarity', 'Latitude', 'Longitude', 'Cliente_Gusta']]

    fig = None
    if plot_3d:
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

    return result, fig

# ----------- INTERFAZ DE STREAMLIT ----------- #
st.set_page_config(page_title="Recomendador Clubers", layout="centered")

st.title("🍽️ Recomendador de Restaurantes - Clubers")

# Sidebar: selección de cliente y opciones
st.sidebar.header("Opciones")
cliente_ids = df_final['NumeroSocioConsumidor'].sort_values().unique()
client_id = st.sidebar.selectbox("Selecciona un cliente", cliente_ids)
num_recs = st.sidebar.slider("Número de recomendaciones", 1, 10, value=5)
plot = st.sidebar.checkbox("Mostrar gráfico 3D")

# Mostrar gráfico de pastel
pie_chart = plot_preference_pie(client_id)
if pie_chart:
    st.pyplot(pie_chart)
else:
    st.warning("Este cliente no tiene preferencias registradas.")

# Botón principal
if st.button("Recomendar"):
    resultados, grafica = recommend_restaurants_for_client_SVD(client_id, n=num_recs, plot_3d=plot)
    if resultados is None:
        st.error(grafica)
    else:
        st.success("¡Recomendaciones generadas exitosamente!")
        st.dataframe(resultados)
        if grafica:
            st.pyplot(grafica)
