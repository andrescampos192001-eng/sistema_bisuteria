import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Configuración de página
st.set_page_config(page_title="💎 BIZUTERIA BRIRODRIGUEZ", page_icon="💍", layout="wide")

# Inicialización segura
@st.cache_resource
def iniciar_conexion():
    url = "https://tqgmapwcknhdydjkbdtj.supabase.co"
    key = st.secrets["SUPABASE_KEY"] # Asegúrate de tener esto en Secrets
    return create_client(url, key)

supabase = iniciar_conexion()

# --- CSS: ESTILO ROSA UNIFICADO ---
st.markdown("""
<style>
    .stApp { background-color: #fdf2f8 !important; }
    h1, h2, h3 { color: #ec4899 !important; font-family: 'Playfair Display', serif; }
    div.stButton > button {
        background-color: #ec4899 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold;
    }
    /* Mejora de visibilidad en móviles */
    @media (max-width: 600px) {
        .stApp { padding: 10px; }
        h1 { font-size: 20px; }
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE TABLAS ---
# Esta función busca la tabla sin importar si escribiste 'Inventario' o 'inventario'
def obtener_datos(tabla):
    try:
        return supabase.table(tabla).select("*").execute().data
    except:
        return []

# --- MENÚ DE CONTROL ---
menu = st.sidebar.selectbox("MENÚ DE CONTROL", 
    ["🏠 Inicio y Gráficos", "➕ Agregar Producto", "📦 Inventario", "💰 Registrar Venta (POS)", "📊 Soporte Contable", "⚙️ Panel Administrador"])

# --- RUTAS DE NAVEGACIÓN ---
if menu == "🏠 Inicio y Gráficos":
    st.title("💎 BIZUTERIA BRIRODRIGUEZ")
    st.write("Dashboard Gerencial")

elif menu == "📦 Inventario":
    st.title("📦 Inventario")
    datos = obtener_datos("Inventario") # Usamos la 'I' mayúscula como en tu captura
    if datos:
        st.dataframe(pd.DataFrame(datos), use_container_width=True)
    else:
        st.warning("No se encontraron datos. Verifica el nombre de la tabla.")

elif menu == "➕ Agregar Producto":
    st.title("➕ Agregar Producto")
    with st.form("form_prod"):
        nombre = st.text_input("Nombre")
        precio = st.number_input("Precio", min_value=0.0)
        stock = st.number_input("Stock", min_value=0)
        if st.form_submit_button("Guardar"):
            # Insertar datos
            supabase.table("Inventario").insert({"nombre": nombre, "precio": str(precio), "stock": stock}).execute()
            st.success("¡Producto agregado con éxito!")