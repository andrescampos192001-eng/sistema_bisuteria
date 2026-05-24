import streamlit as st
import pandas as pd
from supabase import create_client

# Configuración de página
st.set_page_config(page_title="BIZUTERIA BRIRODRIGUEZ", layout="wide")

# Conexión Supabase
@st.cache_resource
def get_supabase():
    url = "https://tqgmapwcknhdydjkbdtj.supabase.co"
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# Estilos CSS (El toque femenino y alineación de tarjetas)
st.markdown("""
<style>
    .stApp { background-color: #fdf2f8 !important; }
    h1, h3 { color: #9d174d !important; font-family: sans-serif; }
    div[data-testid="stMetric"] { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #fbcfe8; }
    div.stButton > button { background-color: #ec4899 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# Menú lateral
menu = st.sidebar.selectbox("💎 MENÚ DE CONTROL", 
    ["🏠 Inicio y Gráficos", "➕ Agregar Producto", "📦 Inventario", "💰 Registrar Venta (POS)", "📊 Soporte Contable", "⚙️ Panel Administrador"])

# --- LÓGICA DE SECCIONES ---

if menu == "🏠 Inicio y Gráficos":
    st.title("💎 JOYERÍA BISUTERÍA BRI RODRÍGUEZ")
    st.subheader("Dashboard Gerencial Automatizado")
    
    # Obtener datos para métricas
    res = supabase.table("Inventario").select("*").execute()
    data = res.data if res.data else []
    total_modelos = len(data)
    total_stock = sum([item.get('stock', 0) for item in data])
    
    # Tarjetas horizontales (igual a tu foto)
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Modelos de Productos", total_modelos)
    col2.metric("💰 Caja Total Recaudada", "$0.00")
    col3.metric("📊 Unidades en Stock", f"{total_stock} unds")
    
    st.info("💡 Los gráficos diferenciados se activarán al registrar las primeras soportes de venta.")

elif menu == "💰 Registrar Venta (POS)":
    st.title("💰 Registrar Venta")
    
    with st.expander("👤 Datos del Cliente", expanded=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre y Apellido")
        doc = c2.text_input("Documento de Identidad")
        direccion = st.text_input("Dirección")
        c3, c4, c5 = st.columns(3)
        ciudad = c3.text_input("Ciudad")
        pais = c4.text_input("País")
        iva = c5.selectbox("¿Responsable de IVA?", ["No", "Sí"])

    st.subheader("🛍️ Carrito y Ajustes")
    c_prod, c_cant, c_desc = st.columns(3)
    # Aquí iría la carga desde Supabase para el selectbox
    producto = c_prod.selectbox("Seleccionar Producto", ["Collares", "Alambres"])
    cantidad = c_cant.number_input("Cantidad", 1)
    descuento = c_desc.selectbox("Descuento (%)", [0, 10, 20, "Personalizado"])
    
    if st.button("Agregar a la factura"):
        st.success("Artículo agregado")
        
    st.write("---")
    st.write("### 🧾 Total Neto a Pagar: $0.00")

elif menu == "📦 Inventario":
    st.title("📦 Inventario")
    res = supabase.table("Inventario").select("*").execute()
    if res.data:
        st.table(pd.DataFrame(res.data))

# (Aquí puedes seguir añadiendo las otras secciones)