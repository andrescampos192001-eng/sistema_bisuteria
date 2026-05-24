import streamlit as st
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from supabase import create_client, Client
import pandas as pd
import io
import time

# =========================================
# CONFIGURACIÓN GENERAL RESPONSIVE
# =========================================
st.set_page_config(
    page_title="💎 BIZUTERIA BRIRODRIGUEZ",
    page_icon="💍",
    layout="wide"
)

# =========================================
# CONEXIÓN SEGURA MEDIANTE SECRETS
# =========================================
@st.cache_resource
def iniciar_conexion_supabase() -> Client:
    SUPABASE_URL = "https://tqgmapwcknhdydjkbdtj.supabase.co"
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    if not SUPABASE_KEY:
        # Clave de respaldo por si acaso
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxZ21hcHdja25oZHlkamtidGRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY4NDA4ODcsImV4cCI6MjAzMjQxNjg4N30.8_9I0LidA2k6Fj_XvWj8v1N_4j_4_9_X_8_9_I0LidA"
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = iniciar_conexion_supabase()
except Exception as e:
    st.error("Error al inicializar el cliente de datos.")

if "carrito" not in st.session_state:
    st.session_state.carrito = []

# =========================================
# CONTROL AUTOMÁTICO DE MAYÚSCULAS EN TABLAS
# =========================================
# Esta función intenta leer la tabla en minúsculas; si falla por esquema, usa Mayúsculas.
def obtener_tabla(nombre_tabla):
    try:
        # Intento estándar en minúsculas
        supabase.table(nombre_tabla).select("count", count="exact").limit(1).execute()
        return nombre_tabla
    except Exception as e:
        if "PGRST205" in str(e) or "Could not find the table" in str(e):
            # Si falla, capitaliza la primera letra (ej: 'inventario' -> 'Inventario')
            return nombre_tabla.capitalize()
        return nombre_tabla

TABLA_INVENTARIO = obtener_tabla("inventario")
TABLA_MAESTRO = obtener_tabla("ventas_maestro")
TABLA_DETALLE = obtener_tabla("ventas_detalle")

# =========================================
# CSS INTERACTIVO: ENFOQUE 100% MÓVIL Y MENÚ INVERTIDO
# =========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

/* --- ESTILOS GENERALES Y RESPONSIVE --- */
.stApp {
    background: linear-gradient(135deg, #fdf2f8, #fce7f3, #ffffff) !important;
    color: #1e293b !important;
    font-family: 'Montserrat', sans-serif !important;
}

/* Ajuste automático de fuentes en móviles */
html, body, [data-testid="stMarkdownContainer"] p, .stApp p, .stApp label, .stApp span {
    color: #1e293b !important;
    font-weight: 600 !important;
    font-size: calc(14px + 0.3vw) !important;
}

h1, [data-testid="stMarkdownContainer"] h1 { 
    font-family: 'Playfair Display', serif !important;
    color: #9d174d !important; 
    font-weight: 700 !important;
    font-size: calc(24px + 1vw) !important;
}

h2, h3, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
    font-family: 'Playfair Display', serif !important;
    color: #c2185b !important;
    font-size: calc(18px + 0.5vw) !important;
}

/* Contenedores e inputs autoajustables */
input, select, textarea, div[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 2px solid #f472b6 !important;
    border-radius: 10px !important;
    font-size: 16px !important;
    padding: 8px !important;
}

div[data-baseweb="select"] * {
    color: #1e293b !important;
}

/* Botones Grandes y Táctiles para Dedos */
div.stButton > button, div[data-testid="stForm"] button {
    background: linear-gradient(90deg, #f43f5e, #ec4899) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    width: 100% !important;
    padding: 14px 20px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    box-shadow: 0px 4px 12px rgba(236, 72, 153, 0.2);
}

/* --- CAMBIO SOLICITADO: MENÚ LATERAL INVERTIDO (FONDO BLANCO, TEXTO NEGRO) --- */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    background-image: none !important;
    border-right: 2px solid #e2e8f0 !important;
}

/* Forzar todo el contenido, títulos y selectores del menú a ser negro sobre fondo blanco */
section[data-testid="stSidebar"] * {
    color: #000000 !important;
}

section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] span {
    color: #000000 !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] {
    border: 2px solid #000000 !important;
    background-color: #f8fafc !important;
}

/* Tarjetas de inventario adaptables */
.card {
    background: #ffffff !important;
    padding: 16px;
    border-radius: 14px;
    margin-bottom: 15px;
    border: 2px solid #fbcfe8;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.02);
    width: 100% !important;
}

.section-title {
    background-color: #ffffff !important;
    padding: 10px 15px;
    border-radius: 10px;
    border-left: 5px solid #ec4899;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# MENÚ NAVEGACIÓN (SIDEBAR INVERTIDO)
# =========================================
st.sidebar.markdown("### 💎 MENU DE CONTROL")
menu = st.sidebar.selectbox(
    "Selecciona una Pantalla:",
    ["🏠 Inicio y Gráficos", "➕ Agregar Producto", "📦 Inventario", "💰 Registrar Venta (POS)", "📊 Soporte Contable", "⚙️ Panel Administrador"]
)

# Auxiliar para formatear errores visuales de la API
def manejar_error_api(e):
    st.error(f"⚠️ Error de comunicación con el almacén: {e}")

# =========================================
# 1. PANTALLA: INICIO Y GRÁFICOS
# =========================================
if menu == "🏠 Inicio y Gráficos":
    st.title("💎 BIZUTERIA BRIRODRIGUEZ")
    st.subheader("Dashboard Gerencial Móvil")
    st.markdown("---")

    try:
        res_inv = supabase.table(TABLA_INVENTARIO).select("stock").execute()
        df_inv_res = pd.DataFrame(res_inv.data)
        
        total_productos = len(df_inv_res)
        total_stock_fisico = int(df_inv_res["stock"].sum()) if not df_inv_res.empty else 0
        
        res_ventas = supabase.table(TABLA_MAESTRO).select("total_facturado").execute()
        df_ventas_res = pd.DataFrame(res_ventas.data)
        total_recaudado = sum(Decimal(str(v)) for v in df_ventas_res["total_facturado"]) if not df_ventas_res.empty else Decimal('0.00')
        
        st.metric("📦 Modelos de Productos", total_productos)
        st.metric("💰 Caja Total Recaudada", f"${total_recaudado:,.2f}")
        st.metric("📊 Unidades en Stock", f"{total_stock_fisico} unds")
        st.markdown("---")

        res_m = supabase.table(TABLA_MAESTRO).select("codigo_soporte, total_facturado").execute()
        res_d = supabase.table(TABLA_DETALLE).select("codigo_soporte, id").execute()
        
        df_m = pd.DataFrame(res_m.data)
        df_d = pd.DataFrame(res_d.data)

        if not df_m.empty and not df_d.empty:
            df_conteo_detalles = df_d.groupby("codigo_soporte").size().reset_index(name="total_articulos")
            df_analisis = pd.merge(df_m, df_conteo_detalles, on="codigo_soporte")
            df_analisis["Total Facturado ($)"] = df_analisis["total_facturado"].astype(float)

            st.markdown('<div class="section-title"><h3>🛍️ Compras Individuales (1 Art.)</h3></div>', unsafe_allow_html=True)
            df_individuales = df_analisis[df_analisis["total_articulos"] == 1]
            if not df_individuales.empty:
                st.metric("Total Facturas Unid.", len(df_individuales))
                st.line_chart(df_individuales.set_index("codigo_soporte")["Total Facturado ($)"], color="#ec4899")

            st.markdown('<div class="section-title"><h3>🛒 Compras Múltiples (2+ Art.)</h3></div>', unsafe_allow_html=True)
            df_multiples = df_analisis[df_analisis["total_articulos"] >= 2]
            if not df_multiples.empty:
                st.metric("Total Facturas Múlt.", len(df_multiples))
                st.bar_chart(df_multiples.set_index("codigo_soporte")["Total Facturado ($)"], color="#db2777")
    except Exception as e:
        manejar_error_api(e)

# =========================================
# 2. PANTALLA: AGREGAR PRODUCTO
# =========================================
elif menu == "➕ Agregar Producto":
    st.title("➕ Nuevas Mercancías")

    with st.form("form_producto"):
        nombre = st.text_input("Nombre único del artículo")
        categoria = st.selectbox("Categoría de Bisutería", ["Collares", "Anillos", "Pulseras", "Aretes"])
        costo_input = st.number_input("Costo de Compra ($)", min_value=0.0, step=0.01, value=0.0)
        precio_input = st.number_input("Precio Vitrina ($)", min_value=0.0, step=0.01, value=0.0)
        stock_input = st.number_input("Existencias Iniciales", min_value=0, step=1, value=0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        guardar = st.form_submit_button("Guardar en Base de Datos")

        if guardar:
            if nombre.strip() == "":
                st.error("El nombre no puede estar vacío.")
            else:
                precio_exacto = str(Decimal(str(precio_input)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                costo_exacto = str(Decimal(str(costo_input)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                
                with st.spinner("Sincronizando..."):
                    try:
                        supabase.table(TABLA_INVENTARIO).insert({
                            "nombre": nombre.strip(), "categoria": categoria,
                            "precio": precio_exacto, "stock": int(stock_input), "costo_compra": costo_exacto
                        }).execute()
                        st.success(f"✔ '{nombre}' guardado con éxito.")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        manejar_error_api(e)

# =========================================
# 3. PANTALLA: INVENTARIO
# =========================================
elif menu == "📦 Inventario":
    st.title("📦 Almacén Físico")

    try:
        res = supabase.table(TABLA_INVENTARIO).select("*").order("nombre").execute()
        df_inv = pd.DataFrame(res.data)

        if df_inv.empty:
            st.warning("El almacén está vacío.")
        else:
            for _, fila in df_inv.iterrows():
                stock_act = int(fila["stock"])
                color_stock = "#22c55e" if stock_act > 3 else "#ef4444"
                alerta = "⚠️ ¡BAJO STOCK!" if stock_act <= 3 else "✅ Abastecido"
                
                st.markdown(f'''
                <div class="card">
                    <span style="float: right; background-color: {color_stock}; padding: 3px 8px; border-radius: 6px; font-size: 11px; color: white;">{alerta}</span>
                    <h3>{fila["nombre"]}</h3>
                    <p>📂 <b>Línea:</b> {fila["categoria"]}</p>
                    <p>💸 <b>Costo:</b> ${Decimal(str(fila["costo_compra"])):,.2f} | 💰 <b>Vitrina:</b> ${Decimal(str(fila["precio"])):,.2f}</p>
                    <p>📦 <b>Disponibilidad:</b> {stock_act} unds</p>
                </div>
                ''', unsafe_allow_html=True)
    except Exception as e:
        manejar_error_api(e)

# =========================================
# 4. PANTALLA: REGISTRAR VENTA (POS)
# =========================================
elif menu == "💰 Registrar Venta (POS)":
    st.title("💰 Terminal POS Móvil")

    try:
        res_v = supabase.table(TABLA_INVENTARIO).select("nombre, precio, stock, categoria, costo_compra").gt("stock", 0).order("nombre").execute()
        df_prod_venta = pd.DataFrame(res_v.data)
    except Exception as e:
        df_prod_venta = pd.DataFrame()

    if not df_prod_venta.empty:
        dict_productos = {
            fila["nombre"]: {
                "precio": Decimal(str(fila["precio"])), "stock": int(fila["stock"]), 
                "categoria": fila["categoria"], "costo": Decimal(str(fila["costo_compra"]))
            } for _, fila in df_prod_venta.iterrows()
        }
        
        st.markdown("### 1. Cliente")
        c_nombre = st.text_input("Nombre y Apellido")
        c_id = st.text_input("Cédula / NIT")
        c_telefono = st.text_input("Teléfono")
        c_ciudad = st.text_input("Ciudad")
        c_direccion = st.text_input("Dirección")
        c_iva = "SÍ" if st.checkbox("¿Responsable de IVA?") else "NO"
        
        st.markdown("---")
        st.markdown("### 2. Pedido")
        prod_seleccionado = st.selectbox("Selecciona artículo:", list(dict_productos.keys()))
        
        info_p = dict_productos[prod_seleccionado]
        st.info(f"💰 Vitrina: ${info_p['precio']:,.2f} | 📦 Disponibles: {info_p['stock']} unds")
        cant_solicitada = st.number_input("Cantidad:", min_value=1, max_value=info_p['stock'], step=1, value=1)
        
        opcion_descuento = st.selectbox(
            "Descuento rápido:",
            ["Ninguno (0%)", "Mayorista (10% OFF)", "Volumen (15% OFF)", "Especial (20% OFF)"]
        )
        
        subtotal_bruto = info_p['precio'] * Decimal(int(cant_solicitada))
        descuento_calculado = Decimal('0.00')
        if "10%" in opcion_descuento: descuento_calculado = subtotal_bruto * Decimal('0.10')
        elif "15%" in opcion_descuento: descuento_calculado = subtotal_bruto * Decimal('0.15')
        elif "20%" in opcion_descuento: descuento_calculado = subtotal_bruto * Decimal('0.20')
        
        subtotal_neto = subtotal_bruto - descuento_calculado
        
        if st.button("🛒 Añadir al Carrito"):
            costo_total_lote = info_p["costo"] * Decimal(int(cant_solicitada))
            st.session_state.carrito.append({
                "producto": prod_seleccionado, "categoria": info_p["categoria"],
                "precio_unitario": info_p["precio"], "cantidad": int(cant_solicitada),
                "descuento": descuento_calculado, "subtotal": subtotal_neto, "costo_total_historico": costo_total_lote
            })
            st.toast("Añadido al carrito")

        st.markdown("---")
        st.markdown("### 🛒 Resumen actual")
        if st.session_state.carrito:
            for idx, item in enumerate(st.session_state.carrito):
                st.markdown(f"**{item['producto']}** ({item['cantidad']} unds) -> *Subtotal: ${item['subtotal']:,.2f}*")
            
            total_factura = sum(i["subtotal"] for i in st.session_state.carrito)
            st.markdown(f"## **Total: ${total_factura:,.2f}**")
            
            if st.button("🚀 Confirmar Venta"):
                if not c_nombre.strip() or not c_id.strip():
                    st.error("Nombre y Cédula obligatorios.")
                else:
                    with st.spinner("Procesando..."):
                        try:
                            cod_soporte = f"FAC-{datetime.now().strftime('%d%H%M%S')}"
                            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            supabase.table(TABLA_MAESTRO).insert({
                                "codigo_soporte": cod_soporte, "fecha_hora": ahora, "cliente_nombre": c_nombre.strip(),
                                "cliente_id": c_id.strip(), "direccion": c_direccion.strip(), "telefono": c_telefono.strip(),
                                "ciudad": c_ciudad.strip(), "responsable_iva": c_iva, "total_facturado": str(total_factura)
                            }).execute()
                            
                            for item in st.session_state.carrito:
                                supabase.table(TABLA_DETALLE).insert({
                                    "codigo_soporte": cod_soporte, "producto": item["producto"], "categoria": item["categoria"],
                                    "precio_unitario": str(item["precio_unitario"]), "cantidad": item["cantidad"],
                                    "descuento_total": str(item["descuento"]), "subtotal": str(item["subtotal"]), "costo_total_historico": str(item["costo_total_historico"])
                                }).execute()
                                
                                nuevo_stk = info_p['stock'] - item["cantidad"]
                                supabase.table(TABLA_INVENTARIO).update({"stock": nuevo_stk}).eq("nombre", item["producto"]).execute()
                                
                            st.success("🎉 ¡Venta guardada!")
                            st.session_state.carrito = []
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            manejar_error_api(e)
            if st.button("🗑️ Vaciar Carrito"):
                st.session_state.carrito = []
                st.rerun()
    else:
        st.warning("No hay productos con stock disponible.")

# =========================================
# 5. PANTALLA: SOPORTE CONTABLE
# =========================================
elif menu == "📊 Soporte Contable":
    st.title("📊 Contabilidad")

    try:
        res_m = supabase.table(TABLA_MAESTRO).select("codigo_soporte, fecha_hora, cliente_nombre").execute()
        res_d = supabase.table(TABLA_DETALLE).select("codigo_soporte, producto, precio_unitario, cantidad, descuento_total, subtotal, costo_total_historico").execute()
        
        df_m = pd.DataFrame(res_m.data)
        df_d = pd.DataFrame(res_d.data)
        
        if not df_m.empty and not df_d.empty:
            df_libros = pd.merge(df_m, df_d, on="codigo_soporte")
            df_libros.columns = ["Nro Factura", "Fecha", "Cliente", "Artículo", "Precio ($)", "Cant", "Desc ($)", "Neto ($)", "Costo Compra ($)"]
            
            df_libros["Neto ($)"] = df_libros["Neto ($)"].astype(float)
            df_libros["Desc ($)"] = df_libros["Desc ($)"].astype(float)
            df_libros["Costo Compra ($)"] = df_libros["Costo Compra ($)"].astype(float)
            
            st.metric("💰 Ingreso Neto", f"${df_libros['Neto ($)'].sum():,.2f}")
            st.metric("💸 Ganancia Bruta Real", f"${(df_libros['Neto ($)'].sum() - df_libros['Costo Compra ($)'].sum()):,.2f}")
            
            st.markdown("#### Historial de Registros")
            st.dataframe(df_libros, use_container_width=True, hide_index=True)
        else:
            st.info("Sin registros contables.")
    except Exception as e:
        manejar_error_api(e)

# =========================================
# 6. PANTALLA: PANEL ADMINISTRADOR
# =========================================
elif menu == "⚙️ Panel Administrador":
    st.title("⚙️ Administración")
    
    try:
        res_a = supabase.table(TABLA_INVENTARIO).select("*").order("nombre").execute()
        df_admin = pd.DataFrame(res_a.data)

        if not df_admin.empty:
            prod_mod = st.selectbox("Selecciona artículo a editar:", df_admin["nombre"].tolist())
            fila_prod = df_admin[df_admin["nombre"] == prod_mod].iloc[0]
            
            with st.form("form_edicion"):
                nuevo_nombre = st.text_input("Editar Nombre", value=fila_prod["nombre"])
                nuevo_costo = st.number_input("Editar Costo ($)", value=float(fila_prod["costo_compra"]))
                nuevo_precio = st.number_input("Editar Precio ($)", value=float(fila_prod["precio"]))
                nuevo_stock = st.number_input("Editar Stock", value=int(fila_prod["stock"]))
                
                if st.form_submit_button("Aplicar Cambios"):
                    try:
                        supabase.table(TABLA_INVENTARIO).update({
                            "nombre": nuevo_nombre.strip(), "precio": str(nuevo_precio),
                            "stock": int(nuevo_stock), "costo_compra": str(nuevo_costo)
                        }).eq("id", int(fila_prod["id"])).execute()
                        st.success("Cambios aplicados.")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        manejar_error_api(e)
    except Exception as e:
        manejar_error_api(e)