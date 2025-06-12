import streamlit as st

# Importa tus módulos de página

import Recomendaciones
import Encuesta
import ModeloPlatillos

# Diccionario de páginas
PAGES = {

    "🍽️ Recomendaciones": Recomendaciones,
    "📋 Encuesta personalizada": Encuesta,
    "Restaurantes más cercanos": ModeloPlatillos
}

# Configuración de página general
st.set_page_config(
    page_title="Clubers Recomendador",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar con navegación
st.sidebar.title("Menú de navegación")
selection = st.sidebar.radio("Ir a la sección:", list(PAGES.keys()))

# Ejecutar la página seleccionada
page = PAGES[selection]
page.run()
