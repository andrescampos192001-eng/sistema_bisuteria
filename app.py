import streamlit as st
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import text  # Motor de conexión moderno y seguro
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
# CONEXIÓN EN LA NUBE MODERNA Y COMPATIBLE
# =========================================
def conectar_db():
    # URL de conexión adaptada para SQLAlchemy (el estándar de Streamlit)
    DATABASE_URL = "postgresql+psycopg2://postgres:Aa1082867687_@db.tqgmapwcknhdydjkbdtj.supabase.co:5432/postgres"
    return st.connection("supabase", type="sql", url=DATABASE_URL)

def inicializar_base_datos():
    try:
        db = conectar_db()
        with db.session as session:
            # Estructura optimizada ejecutada mediante transacciones seguras
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS inventario (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT UNIQUE,
                    categoria TEXT,
                    precio TEXT,
                    stock INTEGER,
                    costo_compra TEXT DEFAULT '0.00'
                )
            """))
            
            session.execute(text("""
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
            """))
            
            session.execute(text("""
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
            """))
            session.commit()
    except Exception as e:
        st.error(f"⚠️ Error al enlazar con Supabase Cloud: {e}")
        st.stop()

# Inicializamos las tablas con el nuevo conector
inicializar_base_datos()

if "carrito" not in st.session_state:
    st.session_state.carrito = []

# =========================================
# CSS INTERACTIVO PREMIUM: MÁXIMO CONTRASTE
# =========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

.stApp {
    background: linear-gradient(135deg, #fdf2f8, #fce7f3, #ffffff) !important;
    color: #1e293b !important;
    font-family: 'Montserrat', sans-serif !important;
}

.stApp p, .stApp label, .stApp span, .stApp div, [data-testid="stMarkdownContainer"] p {
    color: #1e293b !important;
    font-weight: 600 !important;
}

h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { 
    font-family: 'Playfair Display', serif !important;
    color: #9d174d !important; 
    font-weight: 700 !important;
}

input, select, textarea, div[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 2px solid #f472b6 !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] * {
    color: #1e293b !important;
}

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

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fce7f3, #fbcfe8) !important;
    border-right: 1px solid #f472b6;
}
section[data-testid="stSidebar"] * {
    color: #1e293b !important;
}

[data-testid="stMetric"] {
    background-color: #ffffff !important;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #fbcfe8;
    text-align: center;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.03);
}
[data-testid="stMetricLabel"] div {
    color: #475569 !important;
    font-weight: bold !important;
}
[data-testid="stMetricValue"] div {
    color: #9d174d !important;
    font-weight: 700 !important;
}

.card {
    background: #ffffff !important;
    padding: 22px;
    border-radius: 18px;
    margin-bottom: 20px;
    border: 2px solid #fbcfe8;
    box-shadow: 0px 6px 18px rgba(219, 39, 119, 0.05);
}
.card h3 {
    color: #9d174d !important;
    margin-top: 0px;
}
.card p, .card b {
    color: #0f172a !important;
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

    try:
        db = conectar_db()
        total_productos = db.query("SELECT COUNT(*) FROM inventario;").iloc[0, 0]
        
        total_stock_res = db.query("SELECT SUM(stock) FROM inventario;").iloc[0, 0]
        total_stock_fisico = int(total_stock_res) if pd.notna(total_stock_res) else 0
        
        ventas_df = db.query("SELECT total_facturado FROM ventas_maestro;")
        total_recaudado = sum(Decimal(str(v)) for v in ventas_df["total_facturado"]) if not ventas_df.empty else Decimal('0.00')
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Modelos de Productos", total_productos)
        col2.metric("💰 Caja Total Real Recaudada", f"${total_recaudado:,.2f}")
        col3.metric("📊 Unidades en Stock", f"{total_stock_fisico} unds")
        st.markdown("---")

        df_analisis = db.query("""
            SELECT m.codigo_soporte, m.total_facturado, COUNT(d.id) as total_articulos
            FROM ventas_maestro m
            JOIN ventas_detalle d ON m.codigo_soporte = d.codigo_soporte
            GROUP BY m.codigo_soporte, m.total_facturado
        """)

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
    except Exception as e:
        st.error(f"Error de sincronización en Inicio: {e}")

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
                    try:
                        db = conectar_db()
                        with db.session as session:
                            session.execute(
                                text("INSERT INTO inventario (nombre, categoria, precio, stock, costo_compra) VALUES (:nombre, :categoria, :precio, :stock, :costo)"),
                                {"nombre": nombre.strip(), "categoria": categoria, "precio": precio_exacto, "stock": int(stock_input), "costo": costo_exacto}
                            )
                            session.commit()
                        st.success(f"✔ El producto '{nombre}' se ha guardado correctamente.")
                    except Exception as e:
                        st.error(f"❌ Falló el envío (Verifica que el nombre no esté repetido): {e}")

# =========================================
# 3. PANTALLA: INVENTARIO
# =========================================
elif menu == "📦 Inventario":
    st.title("📦 Almacén Físico y Control de Stock")

    try:
        db = conectar_db()
        df_inv = db.query("SELECT nombre, categoria, precio, stock, costo_compra FROM inventario ORDER BY nombre ASC;")

        if df_inv.empty:
            st.warning("El almacén está vacío.")
        else:
            for _, fila in df_inv.iterrows():
                stock_act = int(fila["stock"])
                color_stock = "#22c55e" if stock_act > 3 else "#ef4444"
                alerta_baja = "⚠️ ¡BAJO STOCK!" if stock_act <= 3 else "✅ Abastecido"
                
                st.markdown(f'''
                <div class="card">
                    <span style="float: right; background-color: {color_stock}; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: bold; color: white;">{alerta_baja}</span>
                    <h3>{fila["nombre"]}</h3>
                    <p>📂 <b>Línea de Producto:</b> {fila["categoria"]}</p>
                    <p>💸 <b>Inversión (Costo):</b> ${Decimal(str(fila["costo_compra"])):,.2f} | 💰 <b>Vitrina:</b> ${Decimal(str(fila["precio"])):,.2f}</p>
                    <p>📦 <b>Disponibilidad real:</b> {stock_act} unidades</p>
                </div>
                ''', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al cargar el inventario: {e}")

# =========================================
# 4. PANTALLA: REGISTRAR VENTA (POS)
# =========================================
elif menu == "💰 Registrar Venta (POS)":
    st.title("💰 Terminal de Ventas y Facturación Múltiple")
    st.markdown("---")

    try:
        db = conectar_db()
        df_prod_venta = db.query("SELECT nombre, precio, stock, categoria, costo_compra FROM inventario WHERE stock > 0 ORDER BY nombre ASC;")
    except Exception as e:
        st.error(f"Error al consultar productos: {e}")
        df_prod_venta = pd.DataFrame()

    if not df_prod_venta.empty:
        dict_productos = {
            fila["nombre"]: {
                "precio": Decimal(str(fila["precio"])), 
                "stock": int(fila["stock"]), 
                "categoria": fila["categoria"], 
                "costo": Decimal(str(fila["costo_compra"]))
            } for _, fila in df_prod_venta.iterrows()
        }
        
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
                                try:
                                    db = conectar_db()
                                    cod_soporte = f"FAC-{datetime.now().strftime('%d%H%M%S')}"
                                    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    
                                    with db.session as session:
                                        session.execute(text("""
                                            INSERT INTO ventas_maestro (codigo_soporte, fecha_hora, cliente_nombre, cliente_id, direccion, telefono, ciudad, responsable_iva, total_facturado)
                                            VALUES (:cod, :fecha, :nom, :cid, :dir, :tel, :ciu, :iva, :tot)
                                        """), {"cod": cod_soporte, "fecha": ahora, "nom": c_nombre.strip(), "cid": c_id.strip(), "dir": c_direccion.strip(), "tel": c_telefono.strip(), "ciu": c_ciudad.strip(), "iva": c_iva, "tot": str(total_factura)})
                                        
                                        for item in st.session_state.carrito:
                                            session.execute(text("""
                                                INSERT INTO ventas_detalle (codigo_soporte, producto, categoria, precio_unitario, cantidad, descuento_total, subtotal, costo_total_historico)
                                                VALUES (:cod, :prod, :cat, :pre, :cant, :desc, :sub, :costo)
                                            """), {"cod": cod_soporte, "prod": item["producto"], "cat": item["categoria"], "pre": str(item["precio_unitario"]), "cant": item["cantidad"], "desc": str(item["descuento"]), "sub": str(item["subtotal"]), "costo": str(item["costo_total_historico"])})
                                            
                                            session.execute(text("UPDATE inventario SET stock = stock - :cant WHERE nombre = :prod"), {"cant": item["cantidad"], "prod": item["producto"]})
                                        
                                        session.commit()
                                        
                                    time.sleep(0.4)
                                    st.success(f"🎉 ¡Factura {cod_soporte} guardada!")
                                    st.session_state.carrito = []
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error crítico al registrar la venta: {e}")

# =========================================
# 5. PANTALLA: SOPORTE CONTABLE
# =========================================
elif menu == "📊 Soporte Contable":
    st.title("📊 Libro Mayor de Contabilidad e Ingresos")
    st.markdown("---")

    try:
        db = conectar_db()
        df_libros = db.query("""
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
            ORDER BY m.fecha_hora DESC;
        """)
    except Exception as e:
        st.error(f"Error al conectar con el reporte contable: {e}")
        df_libros = pd.DataFrame()

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
        with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
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
    
    try:
        db = conectar_db()
        df_admin = db.query("SELECT id, nombre, categoria, precio, stock, costo_compra FROM inventario ORDER BY nombre ASC;")
    except Exception as e:
        st.error(f"Error de base de datos: {e}")
        df_admin = pd.DataFrame()

    if df_admin.empty:
        st.info("No hay productos registrados.")
    else:
        nombres_productos = df_admin["nombre"].tolist()
        producto_a_modificar = st.selectbox("Selecciona el producto que deseas gestionar:", nombres_productos)
        
        fila_prod = df_admin[df_admin["nombre"] == producto_a_modificar].iloc[0]
        
        with st.form("form_edicion"):
            nuevo_nombre = st.text_input("Editar Nombre", value=fila_prod["nombre"])
            nueva_categoria = st.selectbox("Editar Categoría", ["Collares", "Anillos", "Pulseras", "Aretes"], index=["Collares", "Anillos", "Pulseras", "Aretes"].index(fila_prod["categoria"]))
            nuevo_costo = st.number_input("Editar Costo Proveedor ($)", min_value=0.0, step=0.01, value=float(fila_prod["costo_compra"]))
            nuevo_precio = st.number_input("Editar Precio Vitrina ($)", min_value=0.0, step=0.01, value=float(fila_prod["precio"]))
            nuevo_stock = st.number_input("Editar Stock", min_value=0, step=1, value=int(fila_prod["stock"]))
            
            if st.form_submit_button("Aplicar Cambios Reales"):
                precio_exacto_ed = str(Decimal(str(nuevo_precio)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                costo_exacto_ed = str(Decimal(str(nuevo_costo)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                
                with st.spinner("Actualizando en la nube..."):
                    try:
                        with db.session as session:
                            session.execute(
                                text("UPDATE inventario SET nombre = :nom, categoria = :cat, precio = :pre, stock = :stk, costo_compra = :cost WHERE id = :id"),
                                {"nom": nuevo_nombre.strip(), "cat": nueva_categoria, "pre": precio_exacto_ed, "stk": int(nuevo_stock), "cost": costo_exacto_ed, "id": int(fila_prod["id"])}
                            )
                            session.commit()
                        st.success("Cambios guardados con éxito.")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudieron guardar los cambios: {e}")