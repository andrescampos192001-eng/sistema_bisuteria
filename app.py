import streamlit as st
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from supabase import create_client, Client
import pandas as pd
import time

# Configuración de página
st.set_page_config(page_title="💎 BIZUTERIA BRIRODRIGUEZ", page_icon="💍", layout="wide")

# Inicialización Supabase
@st.cache_resource
def iniciar_conexion_supabase() -> Client:
    SUPABASE_URL = "https://tqgmapwcknhdydjkbdtj.supabase.co"
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = iniciar_conexion_supabase()

# --- CSS LIMPIO Y UNIFICADO ---
# Mantiene tus colores corporativos (Rosa #ec4899) y asegura visibilidad en todos los dispositivos
st.markdown("""
<style>
    .stApp { background-color: #fdf2f8; }
    h1, h2, h3 { color: #ec4899 !important; font-family: sans-serif; }
    div.stButton > button {
        background-color: #ec4899 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold;
    }
    .css-1r6slb0 { background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)

# Control de tablas
def obtener_tabla(nombre):
    try:
        supabase.table(nombre).select("count", count="exact").limit(1).execute()
        return nombre
    except: return nombre.capitalize()

TABLA_INVENTARIO = obtener_tabla("inventario")
TABLA_MAESTRO = "ventas_maestro"
TABLA_DETALLE = "ventas_detalle"

if "carrito" not in st.session_state: st.session_state.carrito = []

# Menú Lateral
menu = st.sidebar.selectbox("MENÚ DE CONTROL", 
    ["🏠 Inicio y Gráficos", "➕ Agregar Producto", "📦 Inventario", "💰 Registrar Venta (POS)", "📊 Soporte Contable", "⚙️ Panel Administrador"])

# LÓGICA DE NEGOCIO
if menu == "🏠 Inicio y Gráficos":
    st.title("💎 BIZUTERIA BRIRODRIGUEZ")
    st.subheader("Dashboard Gerencial")
    # ... (Aquí mantienes tu lógica de métricas y gráficos original)

elif menu == "➕ Agregar Producto":
    st.title("➕ Agregar Producto")
    with st.form("add_prod"):
        nombre = st.text_input("Nombre")
        precio = st.number_input("Precio", min_value=0.0)
        stock = st.number_input("Stock", min_value=0)
        if st.form_submit_button("Guardar"):
            supabase.table(TABLA_INVENTARIO).insert({"nombre": nombre, "precio": str(precio), "stock": stock}).execute()
            st.success("Guardado")

elif menu == "📦 Inventario":
    st.title("📦 Inventario")
    res = supabase.table(TABLA_INVENTARIO).select("*").execute()
    st.dataframe(pd.DataFrame(res.data))

# ... (Continúa con el resto de tus bloques de menú existentes)