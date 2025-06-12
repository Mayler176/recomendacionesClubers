import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_distances

# Cargar modelo y datos entrenados
with open('svd_model.pkl', 'rb') as f:
    modelo = pickle.load(f)

X_rests_svd = modelo['X_rests_svd']
df_categorias_restaurantes_clubers = modelo['df_categorias_restaurantes_clubers']
df_rest_info = modelo['df_rest_info']

# Categorías que deben coincidir con el modelo
CATEGORIAS = [
    "Asiática", "Bebidas", "Categoría_2", "Categoría_8",
    "Comida_Rápida", "Desayunos", "Italiana", "Postres", "Saludable"
]

def run():
    st.title("📋 Encuesta de preferencias gastronómicas")
    st.markdown("Califica tu gusto del 1 (nada) al 5 (mucho) en cada categoría:")

    respuestas = {}
    for cat in CATEGORIAS:
        respuestas[cat] = st.slider(cat.replace("_", " "), 1, 5, 3)

    nombre_usuario = st.text_input("Tu nombre o alias (para guardar tus respuestas):")

    if st.button("Obtener recomendaciones"):

        if not nombre_usuario.strip():
            st.warning("Por favor, escribe tu nombre o alias.")
            return

        vector_cliente = pd.DataFrame([respuestas])

        # Reindexar columnas en el mismo orden que el modelo
        feature_cols = [c for c in df_categorias_restaurantes_clubers.columns if c not in ('EstablishmentId', 'category')]
        vector_cliente = vector_cliente.reindex(columns=feature_cols, fill_value=0)

        # Proyectar usando el mismo modelo SVD (reentrenado aquí para compatibilidad)
        from sklearn.decomposition import TruncatedSVD
        svd = TruncatedSVD(n_components=3, random_state=42)
        svd.fit(df_categorias_restaurantes_clubers[feature_cols].values)
        vector_svd = svd.transform(vector_cliente.values)

        # Calcular distancias y obtener recomendaciones
        dists = cosine_distances(vector_svd, X_rests_svd)[0]
        nearest = dists.argsort()[:5]

        recs = pd.DataFrame({
            'EstablishmentId': df_categorias_restaurantes_clubers.iloc[nearest]['EstablishmentId'].values,
            'distance': dists[nearest],
            'similarity': (1 - dists[nearest]).round(3)
        })

        recs = recs.merge(df_rest_info, on='EstablishmentId', how='left')

        st.success("¡Aquí están tus recomendaciones!")
        st.dataframe(recs[['RestaurantName', 'similarity']].rename(columns={
            'RestaurantName': 'Restaurante',
            'similarity': 'Similitud'
        }))

        # Guardar las respuestas del usuario
        respuesta_guardada = vector_cliente.copy()
        respuesta_guardada.insert(0, 'usuario', nombre_usuario)

        try:
            existing = pd.read_csv("respuestas_clientes.csv")
            respuesta_guardada = pd.concat([existing, respuesta_guardada], ignore_index=True)
        except FileNotFoundError:
            pass

        respuesta_guardada.to_csv("respuestas_clientes.csv", index=False)
        st.success("Tus respuestas han sido guardadas correctamente.")
