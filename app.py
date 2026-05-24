import streamlit as st
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from supabase import create_client, Client
import pandas as pd
import time

# Configuración de página
st.set_page_config(page_title="💎 BISUTERIA BRI RODRIGUEZ JEWERLY", page_icon="💍", layout="wide")

# Inicialización Supabase (Igual a la tuya)
@st.cache_resource
def iniciar_conexion_supabase() -> Client:
    SUPABASE_URL = "https://tqgmapwcknhdydjkbdtj.supabase.co"
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = iniciar_conexion_supabase()

# --- CSS UNIFICADO PARA PC Y CELULAR ---
st.markdown("""
<style>
    /* Colores corporativos aplicados globalmente */
    :root {
        --color-rosa: #ec4899;
        --color-fondo: #fdf2f8;
        --color-texto: #1f2937;
    }
    
    /* Estructura general */
    .stApp { background-color: var(--color-fondo); }
    
    /* Títulos y textos legibles en ambos dispositivos */
    h1, h2, h3 { color: var(--color-rosa) !important; font-family: 'Playfair Display', serif; }
    
    /* Inputs y Botones con tu estilo rosa */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: 2px solid var(--color-rosa) !important;
        border-radius: 8px !important;
    }
    
    div.stButton > button {
        background-color: var(--color-rosa) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold;
    }
    
    /* Tarjetas de inventario */
    .card {
        background: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid var(--color-rosa);
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Lógica del programa (manteniendo tus tablas)
TABLA_INVENTARIO = "Inventario"
# ... (El resto de tu lógica de negocio sigue igual)