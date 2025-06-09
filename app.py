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

# ----------- FUNCIÓN DE RECOMENDACIÓN ----------- #
def recommend_restaurants_for_client_SVD(client_id, n=5, plot_3d=False):
    idxs = df_final.index[df_final['NumeroSocioConsumidor'] == client_id].tolist()
    if not idxs:
        return None, f"Cliente {client_id} no encontrado."
    
    client_vec_svd = X_clients_svd[idxs[0]].reshape(1, -1)
    dists = cosine_distances(client_vec_svd, X_rests_svd)[0]
    nearest = dists.argsort()[:n]
    
    recs = pd.DataFrame({
        'EstablishmentId': df_categorias_restaurantes_clubers.iloc[nearest]['EstablishmentId'].values,
        'distance': dists[nearest]
    })
    recs['similarity'] = 1 - recs['distance']
    recs = recs.merge(df_rest_info, on='EstablishmentId', how='left')
    result = recs[['RestaurantName', 'distance', 'similarity', 'Latitude', 'Longitude']]
    
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
st.title("🍽️ Recomendador de Restaurantes - Clubers")
st.markdown("Introduce tu ID de cliente para obtener recomendaciones personalizadas.")

client_id = st.number_input("Número de Cliente", min_value=1, step=1)
num_recs = st.slider("¿Cuántas recomendaciones deseas?", 1, 10, value=5)
plot = st.checkbox("Mostrar gráfica 3D de recomendaciones")

if st.button("Recomendar"):
    resultados, grafica = recommend_restaurants_for_client_SVD(client_id, n=num_recs, plot_3d=plot)
    if resultados is None:
        st.error(grafica)
    else:
        st.success("¡Recomendaciones generadas exitosamente!")
        st.dataframe(resultados)
        if grafica:
            st.pyplot(grafica)
