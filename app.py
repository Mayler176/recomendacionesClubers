import streamlit as st

# ⚠️ Este debe ser el primer comando relacionado con Streamlit
st.set_page_config(
    page_title="Clubers Recomendador",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Después puedes importar tus módulos de página
import Recomendaciones
import Encuesta
import ModeloPlatillos

# Diccionario de páginas
PAGES = {
    "🍽️ Recomendaciones": Recomendaciones,
    "📋 Encuesta personalizada": Encuesta,
    "Restaurantes más cercanos": ModeloPlatillos
}

# Sidebar con navegación
st.sidebar.title("Menú de navegación")
selection = st.sidebar.radio("Ir a la sección:", list(PAGES.keys()))

# Ejecutar la página seleccionada
page = PAGES[selection]
page.run()
