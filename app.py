import streamlit as st
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import psycopg2  # Conector oficial para PostgreSQL en la nube
from psycopg2.extras import DictCursor
import pandas as pd
import io
import time

# =========================================
# CONFIGURACIÓN GENERAL
# =========================================
st.set_page_config(
    page_title="💎 BIZUTERIA BRIRODRIGUEZ",
    page_icon="💍",
    layout="wide"
)

# =========================================
# CONEXIÓN EN LA NUBE CON CACHÉ (SUPABASE)
# =========================================
@st.cache_resource
def conectar_db():
    DATABASE_URL = "postgresql://postgres:Aa1082867687_@db.tqgmapwcknhdydjkbdtj.supabase.co:5432/postgres"
    return psycopg2.connect(DATABASE_URL)

def inicializar_base_datos():
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Estructura optimizada para la nube (PostgreSQL)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id SERIAL PRIMARY KEY,
            nombre TEXT UNIQUE,
            categoria TEXT,
            precio TEXT,
            stock INTEGER,
            costo_compra TEXT DEFAULT '0.00'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas_maestro (
            codigo_soporte TEXT PRIMARY KEY,
            fecha_hora TEXT,
            cliente_nombre TEXT,
            cliente_id TEXT,
            direccion TEXT,
            telefono TEXT,
            ciudad TEXT,
            responsable_iva TEXT,
            total_facturado TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas_detalle (
            id SERIAL PRIMARY KEY,
            codigo_soporte TEXT,
            producto TEXT,
            categoria TEXT,
            precio_unitario TEXT,
            cantidad INTEGER,
            descuento_total TEXT,
            subtotal TEXT,
            costo_total_historico TEXT DEFAULT '0.00'
        )
    """)
    conn.commit()

# Inicializamos las tablas directamente en internet
inicializar_base_datos()

if "carrito" not in st.session_state:
    st.session_state.carrito = []

# =========================================
# CSS INTERACTIVO PREMIUM: MÁXIMO CONTRASTE
# =========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

/* FONDO GENERAL CLARO CON TEXTO OSCURO OBLIGATORIO */
.stApp {
    background: linear-gradient(135deg, #fdf2f8, #fce7f3, #ffffff) !important;
    color: #1e293b !important; /* Gris casi negro para lectura perfecta */
    font-family: 'Montserrat', sans-serif !important;
}

/* FORZAR COLOR OSCURO EN TEXTOS DE STREAMLIT, LABELS Y PARÁGRAFOS */
.stApp p, .stApp label, .stApp span, .stApp div, [data-testid="stMarkdownContainer"] p {
    color: #1e293b !important;
    font-weight: 500 !important;
}

/* TÍTULOS EN COLOR ROSADO COMPORTAMIENTO PREMIUM Y VISIBLE */
h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { 
    font-family: 'Playfair Display', serif !important;
    color: #9d174d !important; 
    font-weight: 700 !important;
}

/* CAJAS DE INPUT, SELECCIÓN Y TEXTO (TEXTO INTERNO OSCURO, FONDO BLANCO) */
input, select, textarea, div[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #f472b6 !important;
    border-radius: 10px !important;
}

/* COMPORTAMIENTO INTERNO DE LAS LISTAS DESPLEGABLES */
div[data-baseweb="select"] * {
    color: #1e293b !important;
}

/* BOTONES PREMIUM CON LETRA BLANCA DE ALTO CONTRASTE */
div.stButton > button, div[data-testid="stForm"] button {
    background: linear-gradient(90deg, #f43f5e, #ec4899) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    box-shadow: 0px 4px 12px rgba(236, 72, 153, 0.2);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div.stButton > button:hover {
    background: linear-gradient(90deg, #ec4899, #d946ef) !important;
    color: #ffffff !important;
}

/* SIDEBAR EN COLOR CONTRASTANTE */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fce7f3, #fbcfe8) !important;
    border-right: 1px solid #f472b6;
}
section[data-testid="stSidebar"] * {
    color: #1e293b !important;
}

/* BLOQUES DE MÉTRICAS (NÚMEROS Y TITULOS) */
[data-testid="stMetric"] {
    background-color: #ffffff !important;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #fbcfe8;
    text-align: center;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.03);
}
[data-testid="stMetricLabel"] div {
    color: #64748b !important; /* Gris oscuro para el subtítulo */
}
[data-testid="stMetricValue"] div {
    color: #9d174d !important; /* Rosado oscuro para el número grande */
    font-weight: 700 !important;
}

/* TARJETAS DEL INVENTARIO */
.card {
    background: #ffffff !important;
    padding: 22px;
    border-radius: 18px;
    margin-bottom: 20px;
    border: 1px solid #fbcfe8;
    box-shadow: 0px 6px 18px rgba(219, 39, 119, 0.03);
}
.card h3 {
    color: #9d174d !important;
    margin-top: 0px;
}
.card p, .card b {
    color: #334155 !important;
}

.section-title {
    background-color: #ffffff !important;
    padding: 12px 20px;
    border-radius: 12px;
    border-left: 6px solid #ec4899;
    margin-bottom: 18px;
}
.section-title h3 {
    margin: 0px !important;
    color: #9d174d !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# MENÚ NAVEGACIÓN
# =========================================
st.sidebar.title("💎 MENU DE CONTROL")
menu = st.sidebar.selectbox(
    "Selecciona una Pantalla:",
    ["🏠 Inicio y Gráficos", "➕ Agregar Producto", "📦 Inventario", "💰 Registrar Venta (POS)", "📊 Soporte Contable", "⚙️ Panel Administrador"]
)

# =========================================
# 1. PANTALLA: INICIO Y GRÁFICOS
# =========================================
if menu == "🏠 Inicio y Gráficos":
    st.title("💎 BIZUTERIA BRIRODRIGUEZ")
    st.subheader("Dashboard Gerencial Automatizado")
    st.markdown("---")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventario")
    total_productos = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(stock) FROM inventario")
    total_stock_fisico = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT total_facturado FROM ventas_maestro")
    ventas_db = cursor.fetchall()
    total_recaudado = sum(Decimal(v[0]) for v in ventas_db)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Modelos de Productos", total_productos)
    col2.metric("💰 Caja Total Real Recaudada", f"${total_recaudado:,.2f}")
    col3.metric("📊 Unidades en Stock", f"{total_stock_fisico} unds")
    st.markdown("---")

    df_analisis = pd.read_sql_query("""
        SELECT m.codigo_soporte, m.total_facturado, COUNT(d.id) as total_articulos
        FROM ventas_maestro m
        JOIN ventas_detalle d ON m.codigo_soporte = d.codigo_soporte
        GROUP BY m.codigo_soporte
    """, conn)

    if not df_analisis.empty:
        df_analisis["Total Facturado ($)"] = df_analisis["total_facturado"].astype(float)

        st.markdown('<div class="section-title"><h3>🛍️ Análisis de Compras Individuales (1 Solo Producto)</h3></div>', unsafe_allow_html=True)
        df_individuales = df_analisis[df_analisis["total_articulos"] == 1]
        
        if not df_individuales.empty:
            ci1, ci2 = st.columns([1, 2])
            with ci1:
                st.metric("Total Facturas Individuales", len(df_individuales))
                st.metric("Recaudación Individual Real", f"${df_individuales['Total Facturado ($)'].sum():,.2f}")
            with ci2:
                st.markdown("##### Historial de Ingresos Neto (Factura Única)")
                st.line_chart(df_individuales.set_index("codigo_soporte")["Total Facturado ($)"], color="#ec4899")
        else:
            st.info("Aún no se registran facturas de un solo artículo.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="section-title"><h3>🛒 Análisis de Compras Múltiples (2 o Más Productos)</h3></div>', unsafe_allow_html=True)
        df_multiples = df_analisis[df_analisis["total_articulos"] >= 2]
        
        if not df_multiples.empty:
            cm1, cm2 = st.columns([1, 2])
            with cm1:
                st.metric("Total Facturas Múltiples", len(df_multiples))
                st.metric("Recaudación Múltiple Real", f"${df_multiples['Total Facturado ($)'].sum():,.2f}")
            with cm2:
                st.markdown("##### Volumen de Dinero por Factura Múltiple")
                st.bar_chart(df_multiples.set_index("codigo_soporte")["Total Facturado ($)"], color="#db2777")
        else:
            st.info("Aún no se registran facturas con múltiples artículos variados.")

# =========================================
# 2. PANTALLA: AGREGAR PRODUCTO
# =========================================
elif menu == "➕ Agregar Producto":
    st.title("➕ Registro de Nuevas Mercancías")

    with st.form("form_producto"):
        nombre = st.text_input("Nombre único del artículo")
        categoria = st.selectbox("Categoría de Bisutería", ["Collares", "Anillos", "Pulseras", "Aretes"])
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            costo_input = st.number_input("Costo de Compra Proveedor ($)", min_value=0.0, step=0.01, value=0.0)
        with col_p2:
            precio_input = st.number_input("Precio de Venta Sugerido en Vitrina ($)", min_value=0.0, step=0.01, value=0.0)
            
        stock_input = st.number_input("Existencias Iniciales", min_value=0, step=1, value=0)
        guardar = st.form_submit_button("Guardar en Base de Datos")

        if guardar:
            if nombre.strip() == "":
                st.error("Error: El nombre del artículo no puede quedarse vacío.")
            else:
                precio_exacto = str(Decimal(str(precio_input)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                costo_exacto = str(Decimal(str(costo_input)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                
                with st.spinner("Sincronizando con catálogo en la nube..."):
                    conn = conectar_db()
                    cursor = conn.cursor()
                    try:
                        cursor.execute(
                            "INSERT INTO inventario (nombre, categoria, precio, stock, costo_compra) VALUES (%s, %s, %s, %s, %s)",
                            (nombre.strip(), categoria, precio_exacto, int(stock_input), costo_exacto)
                        )
                        conn.commit()
                        st.success(f"✔ El producto '{nombre}' se ha guardado correctamente.")
                    except psycopg2.IntegrityError:
                        conn.rollback()
                        st.error(f"❌ Ya existe un artículo registrado con el nombre '{nombre}'.")

# =========================================
# 3. PANTALLA: INVENTARIO
# =========================================
elif menu == "📦 Inventario":
    st.title("📦 Almacén Físico y Control de Stock")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, categoria, precio, stock, costo_compra FROM inventario")
    productos = cursor.fetchall()

    if not productos:
        st.warning("El almacén está vacío.")
    else:
        for p in productos:
            color_stock = "#22c55e" if p[3] > 3 else "#ef4444"
            alerta_baja = "⚠️ ¡BAJO STOCK!" if p[3] <= 3 else "✅ Abastecido"
            
            st.markdown(f'''
            <div class="card">
                <span style="float: right; background-color: {color_stock}; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: bold; color: white;">{alerta_baja}</span>
                <h3>{p[0]}</h3>
                <p>📂 <b>Línea de Producto:</b> {p[1]}</p>
                <p>💸 <b>Inversión (Costo):</b> ${Decimal(p[4]):,.2f} | 💰 <b>Vitrina:</b> ${Decimal(p[2]):,.2f}</p>
                <p>📦 <b>Disponibilidad real:</b> {p[3]} unidades</p>
            </div>
            ''', unsafe_allow_html=True)

# =========================================
# 4. PANTALLA: REGISTRAR VENTA (POS)
# =========================================
elif menu == "💰 Registrar Venta (POS)":
    st.title("💰 Terminal de Ventas y Facturación Múltiple")
    st.markdown("---")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio, stock, categoria, costo_compra FROM inventario WHERE stock > 0")
    db_productos = cursor.fetchall()

    if not db_productos:
        st.warning("No hay mercancías con existencias en el almacén para vender.")
    else:
        dict_productos = {p[0]: {"precio": Decimal(p[1]), "stock": int(p[2]), "categoria": p[3], "costo": Decimal(p[4])} for p in db_productos}
        
        col_izq, col_der = st.columns([1.1, 0.9], gap="large")
        
        with col_izq:
            st.markdown("### 1. Datos de Despacho y Cliente")
            c_nombre = st.text_input("Nombre y Apellido")
            c_id = st.text_input("Documento de Identidad / Cédula / NIT")
            
            c1, c2 = st.columns(2)
            with c1:
                c_telefono = st.text_input("Teléfono de Contacto")
                c_ciudad = st.text_input("Ciudad")
            with c2:
                c_direccion = st.text_input("Dirección")
                c_iva_bool = st.checkbox("¿Es Responsable de IVA?", value=False)
                c_iva = "SÍ" if c_iva_bool else "NO"
            
            st.markdown("---")
            st.markdown("### 2. Añadir Joyas al Pedido")
            prod_seleccionado = st.selectbox("Selecciona un artículo:", list(dict_productos.keys()))
            
            info_p = dict_productos[prod_seleccionado]
            st.info(f"💰 Precio regular en Vitrina: ${info_p['precio']:,.2f} | 📦 Disponibles: {info_p['stock']} unidades")
            
            cant_solicitada = st.number_input("Cantidad a despachar:", min_value=1, max_value=info_p['stock'], step=1, value=1)
            
            with st.expander("🛠️ Ajustes Especiales y Descuentos Rápidos", expanded=True):
                opcion_descuento = st.selectbox(
                    "Opciones de descuento rápido:",
                    ["Ninguno (0%)", "Descuento Mayorista (10% OFF)", "Descuento por Volumen / Docena (15% OFF)", "Promoción Especial (20% OFF)", "Monto Fijo Personalizado ($)"]
                )
                
                subtotal_bruto_item = info_p['precio'] * Decimal(int(cant_solicitada))
                descuento_calculado = Decimal('0.00')
                
                if opcion_descuento == "Descuento Mayorista (10% OFF)":
                    descuento_calculado = (subtotal_bruto_item * Decimal('0.10')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                elif opcion_descuento == "Descuento por Volumen / Docena (15% OFF)":
                    descuento_calculado = (subtotal_bruto_item * Decimal('0.15')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                elif opcion_descuento == "Promoción Especial (20% OFF)":
                    descuento_calculado = (subtotal_bruto_item * Decimal('0.20')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                elif opcion_descuento == "Monto Fijo Personalizado ($)":
                    descuento_base_input = st.number_input("Digita el monto exacto a descontar ($):", min_value=0.0, step=0.50, value=0.0)
                    descuento_por_unidad = st.checkbox("¿Aplicar este descuento a cada unidad individualmente?", value=False)
                    
                    descuento_decimal = Decimal(str(descuento_base_input))
                    if descuento_por_unidad:
                        descuento_calculado = (descuento_decimal * Decimal(int(cant_solicitada))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    else:
                        descuento_calculado = descuento_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    
                    if descuento_calculado > subtotal_bruto_item:
                        st.error("❌ El descuento no puede superar el costo total del artículo.")
                        descuento_calculado = subtotal_bruto_item

                subtotal_neto_item = subtotal_bruto_item - descuento_calculado
                
                if descuento_calculado > 0:
                    st.warning(f"🏷️ Ajuste aplicado: Se restarán **${descuento_calculado:,.2f}** al subtotal.")
            
            btn_carrito = st.button("🛒 Añadir al Carrito de Compras")
            if btn_carrito:
                costo_total_lote = info_p["costo"] * Decimal(int(cant_solicitada))
                existe = False
                for item in st.session_state.carrito:
                    if item["producto"] == prod_seleccionado:
                        nueva_cant = item["cantidad"] + int(cant_solicitada)
                        if nueva_cant <= info_p['stock']:
                            item["cantidad"] = nueva_cant
                            nuevo_bruto = info_p['precio'] * nueva_cant
                            item["descuento"] = item["descuento"] + descuento_calculado
                            item["subtotal"] = nuevo_bruto - item["descuento"]
                            item["costo_total_historico"] = item["costo_total_historico"] + costo_total_lote
                            st.toast(f"Cantidad de {prod_seleccionado} actualizada")
                        else:
                            st.error(f"Supera el stock disponible.")
                        existe = True
                        break
                
                if not existe:
                    st.session_state.carrito.append({
                        "producto": prod_seleccionado,
                        "categoria": info_p["categoria"],
                        "precio_unitario": info_p["precio"],
                        "cantidad": int(cant_solicitada),
                        "descuento": descuento_calculado,
                        "subtotal": subtotal_neto_item,
                        "costo_total_historico": costo_total_lote
                    })
                    st.toast(f"✔ {prod_seleccionado} añadido.")

        with col_der:
            st.markdown("### 🛒 Resumen de la Factura en Curso")
            if not st.session_state.carrito:
                st.markdown("<p style='color:#64748b;'>El carrito está vacío.</p>", unsafe_allow_html=True)
            else:
                df_carrito_view = pd.DataFrame([{
                    "Artículo": i["producto"],
                    "Precio Unit.": f"${i['precio_unitario']:,.2f}",
                    "Cant": i["cantidad"],
                    "Descuento": f"-${i['descuento']:,.2f}",
                    "Subtotal Real": f"${i['subtotal']:,.2f}"
                } for i in st.session_state.carrito])
                
                st.dataframe(df_carrito_view, use_container_width=True, hide_index=True)
                
                total_factura = sum(item["subtotal"] for item in st.session_state.carrito)
                st.markdown(f"## **Total Neto a Cobrar: ${total_factura:,.2f}**")
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("🗑️ Vaciar Carrito"):
                        st.session_state.carrito = []
                        st.rerun()
                with c_btn2:
                    if st.button("🚀 Confirmar y Procesar Venta"):
                        if c_nombre.strip() == "" or c_id.strip() == "":
                            st.error("❌ Los campos Nombre y Cédula son obligatorios.")
                        else:
                            with st.spinner("Procesando venta en la nube..."):
                                conn = conectar_db()
                                cursor = conn.cursor()
                                cod_soporte = f"FAC-{datetime.now().strftime('%d%H%M%S')}"
                                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                                try:
                                    cursor.execute("""
                                        INSERT INTO ventas_maestro (codigo_soporte, fecha_hora, cliente_nombre, cliente_id, direccion, telefono, ciudad, responsable_iva, total_facturado)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (cod_soporte, ahora, c_nombre.strip(), c_id.strip(), c_direccion.strip(), c_telefono.strip(), c_ciudad.strip(), c_iva, str(total_factura)))
                                    
                                    for item in st.session_state.carrito:
                                        cursor.execute("""
                                            INSERT INTO ventas_detalle (codigo_soporte, producto, categoria, precio_unitario, cantidad, descuento_total, subtotal, costo_total_historico)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                        """, (cod_soporte, item["producto"], item["categoria"], str(item["precio_unitario"]), item["cantidad"], str(item["descuento"]), str(item["subtotal"]), str(item["costo_total_historico"])))
                                        
                                        cursor.execute("UPDATE inventario SET stock = stock - %s WHERE nombre = %s", (item["cantidad"], item["producto"]))
                                    
                                    conn.commit()
                                    time.sleep(0.4)
                                    st.success(f"🎉 ¡Factura {cod_soporte} guardada!")
                                    st.session_state.carrito = []
                                    st.rerun()
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"Error en base de datos: {e}")

# =========================================
# 5. PANTALLA: SOPORTE CONTABLE
# =========================================
elif menu == "📊 Soporte Contable":
    st.title("📊 Libro Mayor de Contabilidad e Ingresos")
    st.markdown("---")

    conn = conectar_db()
    df_libros = pd.read_sql_query("""
        SELECT m.codigo_soporte AS "Nro Factura",
               m.fecha_hora AS "Fecha",
               m.cliente_nombre AS "Cliente",
               d.producto AS "Artículo",
               d.precio_unitario AS "Precio Vitrina ($)",
               d.cantidad AS "Cant",
               d.descuento_total AS "Descuento ($)",
               d.subtotal AS "Ingreso Neto Real ($)",
               d.costo_total_historico AS "Costo Compra Total ($)"
        FROM ventas_maestro m
        JOIN ventas_detalle d ON m.codigo_soporte = d.codigo_soporte
        ORDER BY m.fecha_hora DESC
    """, conn)

    if df_libros.empty:
        st.info("No se registran movimientos comerciales.")
    else:
        df_libros["Precio Vitrina ($)"] = df_libros["Precio Vitrina ($)"].astype(float)
        df_libros["Descuento ($)"] = df_libros["Descuento ($)"].astype(float)
        df_libros["Ingreso Neto Real ($)"] = df_libros["Ingreso Neto Real ($)"].astype(float)
        df_libros["Costo Compra Total ($)"] = df_libros["Costo Compra Total ($)"].astype(float)
        
        total_efectivo_real = df_libros["Ingreso Neto Real ($)"].sum()
        total_descuentos_concedidos = df_libros["Descuento ($)"].sum()
        total_costo_mercancia = df_libros["Costo Compra Total ($)"].sum()
        utilidad_bruta = total_efectivo_real - total_costo_mercancia
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("💰 Ingreso Neto (Caja Real)", f"${total_efectivo_real:,.2f}")
        col_m2.metric("🏷️ Descuentos Totales", f"${total_descuentos_concedidos:,.2f}")
        col_m3.metric("💸 UTILIDAD BRUTA REAL (Ganancia)", f"${utilidad_bruta:,.2f}", 
                      delta=f"Margen: {((utilidad_bruta/total_efectivo_real)*100 if total_efectivo_real > 0 else 0):,.1f}%")
        
        st.markdown("### 📋 Historial Analítico Completo")
        st.dataframe(df_libros, use_container_width=True, hide_index=True)
        
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_libros.to_excel(writer, index=False, sheet_name='Contabilidad_BriRodriguez')
        
        st.download_button(
            label="📥 Descargar Reporte en Excel (.xlsx)",
            data=buffer_excel.getvalue(),
            file_name=f"Cierre_Utilidades_BriRodriguez_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =========================================
# 6. PANTALLA: PANEL ADMINISTRADOR
# =========================================
elif menu == "⚙️ Panel Administrador":
    st.title("⚙️ Panel de Control Gerencial")
    st.markdown("---")
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, categoria, precio, stock, costo_compra FROM inventario")
    lista_productos = cursor.fetchall()

    if not lista_productos:
        st.info("No hay productos registrados.")
    else:
        nombres_productos = [p[1] for p in lista_productos]
        producto_a_modificar = st.selectbox("Selecciona el producto que deseas gestionar:", nombres_productos)
        
        datos_actuales = next(p for p in lista_productos if p[1] == producto_a_modificar)
        id_prod, nombre_actual, categoria_actual, precio_actual, stock_actual, costo_actual = datos_actuales
        
        with st.form("form_edicion"):
            nuevo_nombre = st.text_input("Editar Nombre", value=nombre_actual)
            nueva_categoria = st.selectbox("Editar Categoría", ["Collares", "Anillos", "Pulseras", "Aretes"], index=["Collares", "Anillos", "Pulseras", "Aretes"].index(categoria_actual))
            nuevo_costo = st.number_input("Editar Costo Proveedor ($)", min_value=0.0, step=0.01, value=float(costo_actual))
            nuevo_precio = st.number_input("Editar Precio Vitrina ($)", min_value=0.0, step=0.01, value=float(precio_actual))
            nuevo_stock = st.number_input("Editar Stock", min_value=0, step=1, value=int(stock_actual))
            
            if st.form_submit_button("Aplicar Cambios Reales"):
                precio_exacto_ed = str(Decimal(str(nuevo_precio)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                costo_exacto_ed = str(Decimal(str(nuevo_costo)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                
                with st.spinner("Actualizando en la nube..."):
                    cursor.execute(
                        "UPDATE inventario SET nombre = %s, categoria = %s, precio = %s, stock = %s, costo_compra = %s WHERE id = %s",
                        (nuevo_nombre.strip(), nueva_categoria, precio_exacto_ed, int(nuevo_stock), costo_exacto_ed, id_prod)
                    )
                    conn.commit()
                    st.success("Cambios guardados con éxito.")