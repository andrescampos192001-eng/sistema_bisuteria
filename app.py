import streamlit as st
import pandas as pd
from supabase import create_client

# Configuración inicial
st.set_page_config(page_title="💎 BIZUTERIA BRIRODRIGUEZ", page_icon="💍", layout="wide")

# Conexión a Supabase
@st.cache_resource
def get_supabase():
    url = "https://tqgmapwcknhdydjkbdtj.supabase.co"
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# Estilos CSS (Tu diseño original)
st.markdown("""
<style>
    .stApp { background-color: #fdf2f8 !important; }
    h1, h2, h3 { color: #9d174d !important; font-family: sans-serif; }
    div.stButton > button { background-color: #ec4899 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- ESTRUCTURA DE MENÚ ORIGINAL ---
menu = st.sidebar.selectbox("💎 MENÚ DE CONTROL", 
    ["🏠 Inicio", "➕ Agregar Producto", "📦 Inventario", "💰 Registrar Venta", "📊 Contabilidad", "⚙️ Administración"])

# --- LÓGICA DE SECCIONES ---

if menu == "🏠 Inicio":
    st.title("💎 BIZUTERIA BRIRODRIGUEZ")
    st.subheader("Dashboard Gerencial Automatizado")
    # Lógica para mostrar métricas rápidas
    res = supabase.table("Inventario").select("id").execute()
    st.metric("Modelos de Productos", len(res.data) if res.data else 0)

elif menu == "➕ Agregar Producto":
    st.title("➕ Agregar Producto")
    with st.form("form_prod"):
        nombre = st.text_input("Nombre del Producto")
        costo = st.number_input("Costo de Compra", 0.0)
        precio = st.number_input("Precio Vitrina", 0.0)
        stock = st.number_input("Existencias Iniciales", 0)
        if st.form_submit_button("Guardar en Base de Datos"):
            supabase.table("Inventario").insert({"nombre": nombre, "costo_compra": costo, "precio": precio, "stock": stock}).execute()
            st.success("Producto guardado correctamente.")

elif menu == "📦 Inventario":
    st.title("📦 Inventario")
    res = supabase.table("Inventario").select("*").execute()
    if res.data:
        st.table(pd.DataFrame(res.data))

elif menu == "💰 Registrar Venta":
    st.title("💰 Registrar Venta (POS)")
    res = supabase.table("Inventario").select("nombre, precio, stock").execute()
    if res.data:
        # Aquí va tu lógica de carrito original
        prod_nombres = [p['nombre'] for p in res.data]
        seleccion = st.selectbox("Selecciona artículo", prod_nombres)
        cantidad = st.number_input("Cantidad", 1)
        if st.button("Procesar Venta"):
            st.write(f"Venta de {cantidad} unidad(es) de {seleccion} registrada.")
    else:
        st.warning("No hay productos disponibles.")

elif menu == "📊 Contabilidad":
    st.title("📊 Soporte Contable")
    st.write("Módulo de reportes financieros habilitado.")

elif menu == "⚙️ Administración":
    st.title("⚙️ Panel Administrador")
    st.write("Configuraciones del sistema y edición de registros.")