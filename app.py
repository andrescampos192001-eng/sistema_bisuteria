import streamlit as st
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from supabase import create_client, Client
import pandas as pd
import time

# =========================================
# CONFIGURACIÓN Y CONEXIÓN
# =========================================
st.set_page_config(page_title="💎 BIZUTERIA BRIRODRIGUEZ", page_icon="💍", layout="wide")

@st.cache_resource
def iniciar_conexion_supabase() -> Client:
    SUPABASE_URL = "https://tqgmapwcknhdydjkbdtj.supabase.co"
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = iniciar_conexion_supabase()

if "carrito" not in st.session_state: st.session_state.carrito = []

# =========================================
# ESTILOS (UNIFICADOS PARA PC Y MÓVIL)
# =========================================
st.markdown("""
<style>
    .stApp { background-color: #fdf2f8 !important; }
    h1, h2, h3 { color: #9d174d !important; font-family: sans-serif; }
    div.stButton > button {
        background: #ec4899 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# =========================================
# NAVEGACIÓN
# =========================================
menu = st.sidebar.selectbox("💎 MENÚ DE CONTROL", 
    ["🏠 Inicio", "➕ Agregar Producto", "📦 Inventario", "💰 Registrar Venta", "📊 Contabilidad", "⚙️ Administración"])

# =========================================
# LÓGICA COMPLETA
# =========================================
if menu == "🏠 Inicio":
    st.title("💎 BIZUTERIA BRIRODRIGUEZ")
    st.write("Bienvenido al sistema. Usa el menú lateral para navegar.")

elif menu == "➕ Agregar Producto":
    st.title("➕ Agregar Producto")
    with st.form("form_prod"):
        nombre = st.text_input("Nombre del producto")
        costo = st.number_input("Costo", 0.0)
        precio = st.number_input("Precio", 0.0)
        stock = st.number_input("Stock inicial", 0)
        if st.form_submit_button("Guardar"):
            supabase.table("Inventario").insert({"nombre": nombre, "costo_compra": str(costo), "precio": str(precio), "stock": stock}).execute()
            st.success("¡Guardado correctamente!")
            st.rerun()

elif menu == "📦 Inventario":
    st.title("📦 Inventario")
    res = supabase.table("Inventario").select("*").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

elif menu == "💰 Registrar Venta":
    st.title("💰 Registrar Venta")
    res = supabase.table("Inventario").select("nombre, precio, stock").gt("stock", 0).execute()
    if res.data:
        prods = {p['nombre']: p for p in res.data}
        sel = st.selectbox("Selecciona artículo", list(prods.keys()))
        cant = st.number_input("Cantidad", 1, prods[sel]['stock'])
        if st.button("Añadir al carrito"):
            st.session_state.carrito.append({"p": sel, "c": cant})
            st.success("Añadido")
        
        if st.session_state.carrito:
            st.write("Carrito:", st.session_state.carrito)
            if st.button("Confirmar Venta"):
                st.write("Procesando...")
                st.session_state.carrito = []
                st.rerun()
    else:
        st.warning("No hay productos disponibles.")

elif menu == "📊 Contabilidad":
    st.title("📊 Contabilidad")
    st.write("Módulo de reportes financieros.")

elif menu == "⚙️ Administración":
    st.title("⚙️ Administración")
    st.write("Configuración del sistema.")