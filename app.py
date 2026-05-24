import streamlit as st
import pandas as pd
from supabase import create_client

# Configuración
st.set_page_config(page_title="💎 BIZUTERIA BRIRODRIGUEZ", page_icon="💍", layout="wide")

@st.cache_resource
def get_supabase():
    url = "https://tqgmapwcknhdydjkbdtj.supabase.co"
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# Estilos CSS - Diseño Femenino y Profesional
st.markdown("""
<style>
    .stApp { background-color: #fdf2f8 !important; }
    h1, h2, h3 { color: #9d174d !important; font-family: 'Helvetica', sans-serif; }
    div.stButton > button { background-color: #ec4899 !important; color: white !important; border-radius: 20px !important; }
    .metric-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #fbcfe8; }
</style>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("💎 MENÚ DE CONTROL", 
    ["🏠 Inicio", "➕ Agregar Producto", "📦 Inventario", "💰 Registrar Venta", "📊 Contabilidad", "⚙️ Administración"])

# --- LÓGICA DE SECCIONES ---

if menu == "🏠 Inicio":
    st.title("💎 BIZUTERIA BRIRODRIGUEZ")
    st.subheader("Dashboard Gerencial")
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    inv = supabase.table("Inventario").select("*").execute().data
    total_stock = sum([i['stock'] for i in inv]) if inv else 0
    
    with col1: st.metric("Modelos de Productos", len(inv) if inv else 0)
    with col2: st.metric("Caja Total Recaudada", "$0.00") # Pendiente de lógica de historial
    with col3: st.metric("Unidades en Stock", total_stock)

elif menu == "💰 Registrar Venta":
    st.title("💰 Registrar Venta (Facturación)")
    
    with st.expander("👤 Datos del Cliente", expanded=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre y Apellido")
        doc = col2.text_input("Documento de Identidad")
        dir = st.text_input("Dirección")
        col3, col4, col5 = st.columns(3)
        ciudad = col3.text_input("Ciudad")
        pais = col4.text_input("País")
        iva = col5.selectbox("¿Responsable de IVA?", ["No", "Sí"])

    st.subheader("🛍️ Carrito de Artículos")
    inv = supabase.table("Inventario").select("nombre, precio").execute().data
    prod_nombres = [p['nombre'] for p in inv]
    
    sel = st.selectbox("Producto", prod_nombres)
    cant = st.number_input("Cantidad a despachar", 1)
    desc = st.selectbox("Descuento (%)", [0, 10, 20, "Personalizado"])
    
    if desc == "Personalizado":
        desc = st.number_input("Ingrese % personalizado", 0, 100)
    
    if st.button("Agregar a la factura"):
        st.success(f"Artículo {sel} agregado al carrito.")
        
    st.subheader("🧾 Resumen de Factura")
    st.write("---")
    st.write("Total Neto a Pagar: $0.00") # Aquí se sumará el cálculo aplicado

elif menu == "➕ Agregar Producto":
    st.title("➕ Agregar Producto")
    with st.form("form_prod"):
        nombre = st.text_input("Nombre")
        precio = st.number_input("Precio", 0.0)
        stock = st.number_input("Stock", 0)
        if st.form_submit_button("Guardar"):
            supabase.table("Inventario").insert({"nombre": nombre, "precio": precio, "stock": stock}).execute()
            st.success("Guardado")

# Resto de secciones (Inventario, etc.) se mantienen igual...