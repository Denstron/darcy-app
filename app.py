import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ── Configuración ──────────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_URL = "https://docs.google.com/spreadsheets/d/1InoW_Xvb5KUGlvbJnOV6zaOAik706ZoV4FwSJIx-xzU/edit"

st.set_page_config(page_title="Darcy", page_icon="🌿", layout="wide")

# ── Estilos ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #fff8f9 !important; }
    [data-testid="stSidebar"] { background-color: #fce4ec !important; }
    [data-testid="stSidebar"] * { color: #880e4f !important; }
    h1, h2, h3 { color: #c2185b !important; }
    p, span, div, label, li, td, th { color: #333333 !important; }
    [data-testid="stMetricValue"] { color: #c2185b !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #555555 !important; }
    .stButton > button {
        background-color: #e91e8c !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 8px 20px !important;
    }
    .stButton > button:hover { background-color: #c2185b !important; }
    [data-testid="stForm"] {
        background: white !important;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #f8bbd0;
        box-shadow: 0 2px 8px rgba(233,30,140,0.08);
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label { color: #880e4f !important; font-weight: 600 !important; }
    [data-testid="stSuccess"] { background-color: #e8f5e9 !important; }
    [data-testid="stInfo"] { background-color: #fce4ec !important; }
    .stRadio label { color: #880e4f !important; font-weight: 500 !important; }
    [data-testid="stExpander"] { border: 1px solid #f8bbd0 !important; border-radius: 8px !important; background-color: white !important; }
    [data-testid="stDataFrame"] * { color: #333333 !important; }
    [data-testid="stMarkdownContainer"] p { color: #333333 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #880e4f !important; }
    input, textarea, select { background-color: #ffffff !important; color: #333333 !important; }
    [data-baseweb="input"] input { background-color: #ffffff !important; color: #333333 !important; }
    [data-baseweb="select"] { background-color: #ffffff !important; }
    [data-baseweb="select"] * { color: #333333 !important; }
    [data-testid="stNumberInput"] input { background-color: #ffffff !important; color: #333333 !important; }
    [data-testid="stTextInput"] input { background-color: #ffffff !important; color: #333333 !important; }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #333333 !important; }
    ul[role="listbox"] { background-color: #ffffff !important; }
    ul[role="listbox"] li { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# ── Login ──────────────────────────────────────────────────────────────────────
def check_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.usuario_actual = ""

    if st.session_state.autenticado:
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("LOGO.jpeg", use_container_width=True)
        except:
            st.markdown("## 🌿 Darcy")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Acceso privado")

        USUARIOS = {
            "Denstron": "danieL0205",
            "Darcy": "Darcy0205"
        }

        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")

        if st.button("Entrar", use_container_width=True):
            if usuario in USUARIOS and clave == USUARIOS[usuario]:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = usuario
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    return False

if not check_password():
    st.stop()

# ── Conexión Google Sheets ─────────────────────────────────────────────────────
@st.cache_resource
def conectar_sheets():
    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
    else:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=SCOPES)
    cliente = gspread.authorize(creds)
    return cliente.open_by_url(SHEET_URL)

def get_ws(sheet, nombre):
    return sheet.worksheet(nombre)

def get_config(sheet):
    cfg = sheet.worksheet("CONFIG").get_all_records()
    return {row["clave"]: float(row["valor"]) for row in cfg}

def get_config_flores(sheet):
    cfg = sheet.worksheet("CONFIG_FLORES").get_all_records()
    return {row["clave"]: float(row["valor"]) for row in cfg}

def get_inventario(sheet):
    return sheet.worksheet("INVENTARIO").get_all_records()

def get_ventas(sheet):
    return sheet.worksheet("VENTAS").get_all_records()

def get_ventas_flores(sheet):
    return sheet.worksheet("VENTAS_FLORES").get_all_records()

def get_compras(sheet):
    return sheet.worksheet("COMPRAS").get_all_records()

def get_compras_flores(sheet):
    return sheet.worksheet("COMPRAS_FLORES").get_all_records()

def get_clientes(sheet):
    return sheet.worksheet("CLIENTES").get_all_records()

def get_pedidos(sheet):
    return sheet.worksheet("PEDIDOS_PENDIENTES").get_all_records()

def actualizar_inventario(sheet, producto, delta, fecha):
    inv_ws = sheet.worksheet("INVENTARIO")
    inv_data = inv_ws.get_all_records()
    for i, row in enumerate(inv_data):
        if row["producto"] == producto:
            nueva_cantidad = int(row["cantidad"]) + delta
            inv_ws.update_cell(i + 2, 2, nueva_cantidad)
            inv_ws.update_cell(i + 2, 3, fecha)
            break

def registrar_cliente_si_nuevo(sheet, nombre, telefono):
    clientes_ws = sheet.worksheet("CLIENTES")
    nombres = [c["nombre"] for c in clientes_ws.get_all_records()]
    if nombre not in nombres:
        clientes_ws.append_row([nombre, telefono])

# ── App ────────────────────────────────────────────────────────────────────────
sheet = conectar_sheets()

try:
    st.sidebar.image("LOGO.jpeg", use_container_width=True)
except:
    st.sidebar.markdown("## 🌿 Darcy")

nombre_usuario = "Denstron" if st.session_state.usuario_actual == "Darcy" else "Daniel"
st.sidebar.markdown(f"**Hola, {nombre_usuario} 👋**")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🌿 Desodorante")
menu_deso = st.sidebar.radio("", [
    "📊 Dashboard Darcy",
    "📦 Inventario",
    "🛒 Registrar Compra",
    "💰 Registrar Venta",
    "👥 Clientes",
    "⏳ Pedidos Pendientes"
], key="menu_deso")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌸 Flores")
menu_flores = st.sidebar.radio("", [
    "📊 Dashboard Flores",
    "🌸 Registrar Venta Flor",
    "🛒 Registrar Compra Material",
    "📦 Historial Flores"
], key="menu_flores")

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.autenticado = False
    st.rerun()

# Determinar qué menú está activo
if "menu_activo" not in st.session_state:
    st.session_state.menu_activo = "deso"

# Detectar cuál se usó último
if "prev_deso" not in st.session_state:
    st.session_state.prev_deso = menu_deso
if "prev_flores" not in st.session_state:
    st.session_state.prev_flores = menu_flores

if menu_deso != st.session_state.prev_deso:
    st.session_state.menu_activo = "deso"
    st.session_state.prev_deso = menu_deso
elif menu_flores != st.session_state.prev_flores:
    st.session_state.menu_activo = "flores"
    st.session_state.prev_flores = menu_flores

menu = menu_deso if st.session_state.menu_activo == "deso" else menu_flores

PRODUCTOS = ["Tarro mediano", "Tarrito spray vacío", "Tarrito spray lleno"]
PRECIOS_KEY = {
    "Tarro mediano": ("costo_tarro_mediano", "precio_tarro_mediano"),
    "Tarrito spray vacío": ("costo_tarrito_spray_vacio", "precio_tarrito_spray_vacio"),
    "Tarrito spray lleno": ("costo_tarrito_spray_lleno", "precio_tarrito_spray_lleno"),
}

TIPOS_FLOR = ["Flor grande", "Flor mediana", "Flor pequeña", "Pedido personalizado"]
FLORES_CONFIG_KEY = {
    "Flor grande": ("costo_flor_grande", "precio_flor_grande"),
    "Flor mediana": ("costo_flor_mediana", "precio_flor_mediana"),
    "Flor pequeña": ("costo_flor_pequena", "precio_flor_pequena"),
    "Pedido personalizado": ("costo_flor_pedido", "precio_flor_pedido"),
}

# ══════════════════════════════════════════════════════════════════════════════
# 📊 DASHBOARD DESODORANTE
# ══════════════════════════════════════════════════════════════════════════════
if menu == "📊 Dashboard Darcy":
    st.title("📊 Darcy — Panel de Control")

    config = get_config(sheet)
    ventas = get_ventas(sheet)
    compras = get_compras(sheet)
    inventario = get_inventario(sheet)

    precios_costo = {p: config[k[0]] for p, k in PRECIOS_KEY.items() if k[0] in config}

    total_vendido = 0
    total_ganancia = 0
    total_pendiente = 0

    for v in ventas:
        cantidad = int(v["cantidad"])
        precio = float(v["precio_unitario_venta"])
        producto = v["producto"]
        ingreso = cantidad * precio
        abonado = float(v.get("abonado", 0) or 0)
        total_vendido += ingreso

        if v["estado_pago"] == "pendiente":
            saldo = ingreso - abonado
            total_pendiente += saldo
            costo_total_venta = precios_costo.get(producto, 0) * cantidad
            if ingreso > 0:
                proporcion_pagada = abonado / ingreso
                total_ganancia += (ingreso - costo_total_venta) * proporcion_pagada
        else:
            ganancia = (precio - precios_costo.get(producto, 0)) * cantidad
            total_ganancia += ganancia

    total_invertido = sum(
        int(c["cantidad"]) * float(c["precio_unitario"]) + float(c["gasto_envio"])
        for c in compras
    ) if compras else 0

    reinvertir = total_ganancia * (config["porcentaje_reinversion"] / 100)
    libre = total_ganancia - reinvertir

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Total vendido", f"${total_vendido:,.0f}")
    col2.metric("📈 Ganancia neta", f"${total_ganancia:,.0f}")
    col3.metric("⏳ Por cobrar", f"${total_pendiente:,.0f}")
    col4.metric("💰 Total invertido", f"${total_invertido:,.0f}")

    st.markdown("---")
    col5, col6 = st.columns(2)
    col5.metric(f"🔄 Reinvertir ({int(config['porcentaje_reinversion'])}%)", f"${reinvertir:,.0f}")
    col6.metric("🎉 Ganancia libre", f"${libre:,.0f}")

    st.markdown("---")
    st.subheader("📦 Inventario actual")
    cols = st.columns(len(inventario))
    for i, item in enumerate(inventario):
        cantidad = int(item["cantidad"])
        color = "🟢" if cantidad > 3 else "🟡" if cantidad > 0 else "🔴"
        cols[i].metric(f"{color} {item['producto']}", f"{cantidad} unidades")

    if ventas:
        st.markdown("---")
        st.subheader("📊 Ventas por producto")
        df_ventas = pd.DataFrame(ventas)
        df_ventas["cantidad"] = df_ventas["cantidad"].astype(int)
        df_ventas["total"] = df_ventas["cantidad"] * df_ventas["precio_unitario_venta"].astype(float)
        resumen = df_ventas.groupby("producto")["total"].sum().reset_index()
        resumen.columns = ["Producto", "Total vendido ($)"]
        st.bar_chart(resumen.set_index("Producto"))

        st.markdown("---")
        col_h1, col_h2 = st.columns([3, 1])
        col_h1.subheader("📋 Últimas ventas")
        ver_todo = col_h2.checkbox("Ver todas")
        df_show = df_ventas[["fecha", "producto", "cantidad", "cliente", "estado_pago", "precio_unitario_venta"]].copy()
        df_show.columns = ["Fecha", "Producto", "Cantidad", "Cliente", "Estado", "Precio unit."]
        df_show = df_show.iloc[::-1]
        if not ver_todo:
            df_show = df_show.head(15)
        st.dataframe(df_show, use_container_width=True)
    else:
        st.info("Aún no hay ventas registradas.")

# ══════════════════════════════════════════════════════════════════════════════
# 📊 DASHBOARD FLORES
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📊 Dashboard Flores":
    st.title("🌸 Flores — Panel de Control")

    cfg_flores = get_config_flores(sheet)
    ventas_flores = get_ventas_flores(sheet)
    compras_flores = get_compras_flores(sheet)

    total_vendido_f = 0
    total_ganancia_f = 0
    total_pendiente_f = 0

    for v in ventas_flores:
        cantidad = int(v["cantidad"])
        precio = float(v["precio_unitario"])
        costo = float(v["costo_unitario"])
        ingreso = cantidad * precio
        abonado = float(v.get("abonado", 0) or 0)
        total_vendido_f += ingreso

        if v["estado_pago"] == "pendiente":
            total_pendiente_f += (ingreso - abonado)
            if ingreso > 0:
                proporcion = abonado / ingreso
                total_ganancia_f += (ingreso - costo * cantidad) * proporcion
        else:
            total_ganancia_f += (precio - costo) * cantidad

    total_invertido_f = sum(
        int(c["cantidad"]) * float(c["precio_unitario"])
        for c in compras_flores
    ) if compras_flores else 0

    reinvertir_f = total_ganancia_f * (cfg_flores.get("porcentaje_reinversion_flores", 60) / 100)
    libre_f = total_ganancia_f - reinvertir_f

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Total vendido", f"${total_vendido_f:,.0f}")
    col2.metric("📈 Ganancia neta", f"${total_ganancia_f:,.0f}")
    col3.metric("⏳ Por cobrar", f"${total_pendiente_f:,.0f}")
    col4.metric("💰 Invertido en materiales", f"${total_invertido_f:,.0f}")

    st.markdown("---")
    col5, col6 = st.columns(2)
    col5.metric("🔄 Reinvertir (60%)", f"${reinvertir_f:,.0f}")
    col6.metric("🎉 Ganancia libre", f"${libre_f:,.0f}")

    if ventas_flores:
        st.markdown("---")
        st.subheader("📊 Ventas por tipo de flor")
        df_f = pd.DataFrame(ventas_flores)
        df_f["cantidad"] = df_f["cantidad"].astype(int)
        df_f["total"] = df_f["cantidad"] * df_f["precio_unitario"].astype(float)
        resumen_f = df_f.groupby("tipo_flor")["total"].sum().reset_index()
        resumen_f.columns = ["Tipo", "Total vendido ($)"]
        st.bar_chart(resumen_f.set_index("Tipo"))

        st.markdown("---")
        col_h1, col_h2 = st.columns([3, 1])
        col_h1.subheader("📋 Últimas ventas")
        ver_todo_f = col_h2.checkbox("Ver todas", key="ver_flores")
        df_show_f = df_f[["fecha", "tipo_flor", "cantidad", "precio_unitario", "cliente", "estado_pago", "nota"]].copy()
        df_show_f.columns = ["Fecha", "Tipo", "Cantidad", "Precio unit.", "Cliente", "Estado", "Nota"]
        df_show_f = df_show_f.iloc[::-1]
        if not ver_todo_f:
            df_show_f = df_show_f.head(15)
        st.dataframe(df_show_f, use_container_width=True)
    else:
        st.info("Aún no hay ventas de flores registradas.")

# ══════════════════════════════════════════════════════════════════════════════
# 📦 INVENTARIO DESODORANTE
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📦 Inventario":
    st.title("📦 Inventario Desodorante")
    inventario = get_inventario(sheet)
    cols = st.columns(len(inventario))
    for i, item in enumerate(inventario):
        with cols[i]:
            cantidad = int(item["cantidad"])
            color = "🟢" if cantidad > 3 else "🟡" if cantidad > 0 else "🔴"
            st.metric(f"{color} {item['producto']}", f"{cantidad} unidades")
            if item["ultima_actualizacion"]:
                st.caption(f"Última actualización: {item['ultima_actualizacion']}")
    st.markdown("---")
    st.dataframe(pd.DataFrame(inventario), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 🛒 REGISTRAR COMPRA DESODORANTE
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "🛒 Registrar Compra":
    st.title("🛒 Registrar Compra Desodorante")
    st.caption("Cada vez que comprás desde Montería, registrá acá.")

    with st.form("form_compra"):
        producto = st.selectbox("Producto", PRODUCTOS)
        cantidad = st.number_input("Cantidad comprada", min_value=1, step=1)
        precio_unitario = st.number_input("Precio unitario ($)", min_value=0.0, step=100.0)
        gasto_envio = st.number_input("Gasto de envío ($)", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Registrar compra", use_container_width=True)

    if submitted:
        costo_total = (cantidad * precio_unitario) + gasto_envio
        costo_real_unitario = costo_total / cantidad
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.worksheet("COMPRAS").append_row([fecha, producto, int(cantidad), precio_unitario, gasto_envio])
        actualizar_inventario(sheet, producto, int(cantidad), fecha)
        st.success("✅ Compra registrada correctamente")
        st.info(f"""
        **Resumen:**
        - Producto: {producto} — {int(cantidad)} unidades
        - Inversión total: ${costo_total:,.0f}
        - Costo real por unidad: ${costo_real_unitario:,.0f}
        """)

# ══════════════════════════════════════════════════════════════════════════════
# 💰 REGISTRAR VENTA DESODORANTE
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "💰 Registrar Venta":
    st.title("💰 Registrar Venta Desodorante")

    config = get_config(sheet)
    inventario = get_inventario(sheet)
    inv_dict = {item["producto"]: int(item["cantidad"]) for item in inventario}
    precios_venta = {p: config[k[1]] for p, k in PRECIOS_KEY.items() if k[1] in config}
    precios_costo = {p: config[k[0]] for p, k in PRECIOS_KEY.items() if k[0] in config}

    clientes_existentes = get_clientes(sheet)
    nombres_existentes = sorted([c["nombre"] for c in clientes_existentes])
    opciones_cliente = ["➕ Cliente nuevo"] + nombres_existentes
    seleccion = st.selectbox("Cliente", opciones_cliente)

    with st.form("form_venta"):
        if seleccion == "➕ Cliente nuevo":
            cliente = st.text_input("Nombre del cliente nuevo")
            telefono = st.text_input("Teléfono (opcional)")
        else:
            cliente = seleccion
            tel_actual = next((c.get("telefono", "") for c in clientes_existentes if c["nombre"] == seleccion), "")
            st.caption(f"Cliente: **{cliente}** {'— ' + tel_actual if tel_actual else ''}")
            telefono = tel_actual

        producto = st.selectbox("Producto", PRODUCTOS)
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        estado_pago = st.selectbox("Estado del pago", ["pagado", "pendiente"])
        abono_inicial = 0.0
        if estado_pago == "pendiente":
            abono_inicial = st.number_input("Abono inicial ($) — dejar en 0 si no abonó nada", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Registrar venta", use_container_width=True)

    if submitted:
        if not cliente:
            st.error("Escribí el nombre del cliente.")
        elif inv_dict.get(producto, 0) < cantidad:
            st.error(f"No hay suficiente inventario. Tenés {inv_dict.get(producto, 0)} unidades de {producto}.")
        else:
            precio_unit = precios_venta[producto]
            costo_unit = precios_costo[producto]
            ganancia = (precio_unit - costo_unit) * cantidad
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
            total_venta = precio_unit * cantidad
            if estado_pago == "pagado":
                abono_inicial = total_venta

            sheet.worksheet("VENTAS").append_row([fecha, producto, int(cantidad), cliente, estado_pago, precio_unit, abono_inicial])
            actualizar_inventario(sheet, producto, -int(cantidad), fecha)
            registrar_cliente_si_nuevo(sheet, cliente, telefono)

            st.success("✅ Venta registrada")
            st.info(f"""
            **Resumen:**
            - Cliente: {cliente} — {producto} × {int(cantidad)}
            - Total: ${total_venta:,.0f} | Abonado: ${abono_inicial:,.0f} | Saldo: ${(total_venta - abono_inicial):,.0f}
            - Ganancia: ${ganancia:,.0f} | Estado: {estado_pago}
            """)

# ══════════════════════════════════════════════════════════════════════════════
# 🌸 REGISTRAR VENTA FLOR
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "🌸 Registrar Venta Flor":
    st.title("🌸 Registrar Venta de Flor")

    cfg_flores = get_config_flores(sheet)
    clientes_existentes = get_clientes(sheet)
    nombres_existentes = sorted([c["nombre"] for c in clientes_existentes])
    opciones_cliente = ["➕ Cliente nuevo"] + nombres_existentes
    seleccion = st.selectbox("Cliente", opciones_cliente, key="sel_cliente_flor")

    with st.form("form_venta_flor"):
        if seleccion == "➕ Cliente nuevo":
            cliente = st.text_input("Nombre del cliente nuevo")
            telefono = st.text_input("Teléfono (opcional)")
        else:
            cliente = seleccion
            tel_actual = next((c.get("telefono", "") for c in clientes_existentes if c["nombre"] == seleccion), "")
            st.caption(f"Cliente: **{cliente}** {'— ' + tel_actual if tel_actual else ''}")
            telefono = tel_actual

        tipo_flor = st.selectbox("Tipo de flor", TIPOS_FLOR)

        # Precio y costo sugerido según tipo
        costo_key, precio_key = FLORES_CONFIG_KEY[tipo_flor]
        precio_sugerido = cfg_flores.get(precio_key, 0.0)
        costo_sugerido = cfg_flores.get(costo_key, 0.0)

        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio_unitario = st.number_input(
            "Precio de venta por unidad ($)",
            min_value=0.0,
            value=precio_sugerido,
            step=1000.0
        )
        costo_unitario = st.number_input(
            "Costo de materiales por unidad ($)",
            min_value=0.0,
            value=costo_sugerido,
            step=1000.0
        )
        estado_pago = st.selectbox("Estado del pago", ["pagado", "pendiente"])
        abono_inicial = 0.0
        if estado_pago == "pendiente":
            abono_inicial = st.number_input("Abono inicial ($)", min_value=0.0, step=1000.0)
        nota = st.text_input("Nota (opcional — ej: colores, detalles del pedido)")
        submitted = st.form_submit_button("Registrar venta", use_container_width=True)

    if submitted:
        if not cliente:
            st.error("Escribí el nombre del cliente.")
        elif precio_unitario == 0:
            st.error("El precio no puede ser $0.")
        else:
            total_venta = precio_unitario * cantidad
            ganancia = (precio_unitario - costo_unitario) * cantidad
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
            if estado_pago == "pagado":
                abono_inicial = total_venta

            sheet.worksheet("VENTAS_FLORES").append_row([
                fecha, tipo_flor, int(cantidad), precio_unitario,
                costo_unitario, cliente, estado_pago, abono_inicial, nota
            ])
            registrar_cliente_si_nuevo(sheet, cliente, telefono)

            st.success("✅ Venta de flor registrada")
            st.info(f"""
            **Resumen:**
            - Cliente: {cliente} — {tipo_flor} × {int(cantidad)}
            - Total: ${total_venta:,.0f} | Abonado: ${abono_inicial:,.0f} | Saldo: ${(total_venta - abono_inicial):,.0f}
            - Ganancia estimada: ${ganancia:,.0f} | Estado: {estado_pago}
            {'- Nota: ' + nota if nota else ''}
            """)

# ══════════════════════════════════════════════════════════════════════════════
# 🛒 REGISTRAR COMPRA MATERIAL FLORES
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "🛒 Registrar Compra Material":
    st.title("🛒 Registrar Compra de Materiales")
    st.caption("Limpia pipas, papel coreano, cinta floral, etc.")

    MATERIALES = ["Limpia pipas", "Cinta floral", "Palillos", "Barra de silicona", "Papel coreano", "Listón para moño", "Tarjeta", "Otro"]

    with st.form("form_compra_flores"):
        material = st.selectbox("Material", MATERIALES)
        if material == "Otro":
            material = st.text_input("Especificá el material")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio_unitario = st.number_input("Precio unitario ($)", min_value=0.0, step=100.0)
        submitted = st.form_submit_button("Registrar compra", use_container_width=True)

    if submitted:
        total = cantidad * precio_unitario
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.worksheet("COMPRAS_FLORES").append_row([fecha, material, int(cantidad), precio_unitario, total])
        st.success(f"✅ Compra registrada — Total: ${total:,.0f}")

# ══════════════════════════════════════════════════════════════════════════════
# 📦 HISTORIAL FLORES
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📦 Historial Flores":
    st.title("📦 Historial de Flores")

    tab1, tab2 = st.tabs(["🌸 Ventas", "🛒 Compras de materiales"])

    with tab1:
        ventas_flores = get_ventas_flores(sheet)
        if not ventas_flores:
            st.info("Aún no hay ventas de flores registradas.")
        else:
            df = pd.DataFrame(ventas_flores)
            df["cantidad"] = df["cantidad"].astype(int)
            df["total"] = df["cantidad"] * df["precio_unitario"].astype(float)
            df["ganancia"] = (df["precio_unitario"].astype(float) - df["costo_unitario"].astype(float)) * df["cantidad"]
            st.dataframe(df.iloc[::-1], use_container_width=True)

    with tab2:
        compras_flores = get_compras_flores(sheet)
        if not compras_flores:
            st.info("Aún no hay compras de materiales registradas.")
        else:
            st.dataframe(pd.DataFrame(compras_flores).iloc[::-1], use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 👥 CLIENTES
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "👥 Clientes":
    st.title("👥 Clientes")

    clientes = get_clientes(sheet)
    ventas_ws = sheet.worksheet("VENTAS")
    ventas_raw = ventas_ws.get_all_values()
    ventas_flores_ws = sheet.worksheet("VENTAS_FLORES")
    ventas_flores_raw = ventas_flores_ws.get_all_values()

    if not clientes:
        st.info("Aún no hay clientes registrados.")
    else:
        headers = ventas_raw[0] if ventas_raw else []
        filas = ventas_raw[1:] if len(ventas_raw) > 1 else []

        idx_fecha = headers.index("fecha") if "fecha" in headers else 0
        idx_producto = headers.index("producto") if "producto" in headers else 1
        idx_cantidad = headers.index("cantidad") if "cantidad" in headers else 2
        idx_cliente = headers.index("cliente") if "cliente" in headers else 3
        idx_estado = headers.index("estado_pago") if "estado_pago" in headers else 4
        idx_precio = headers.index("precio_unitario_venta") if "precio_unitario_venta" in headers else 5
        idx_abonado = headers.index("abonado") if "abonado" in headers else None

        headers_f = ventas_flores_raw[0] if ventas_flores_raw else []
        filas_f = ventas_flores_raw[1:] if len(ventas_flores_raw) > 1 else []

        for cliente in clientes:
            nombre = cliente["nombre"]
            tel = cliente.get("telefono", "")

            filas_cliente = [(i, f) for i, f in enumerate(filas) if len(f) > idx_cliente and f[idx_cliente] == nombre]
            filas_flores_cliente = [(i, f) for i, f in enumerate(filas_f) if len(f) > 5 and f[5] == nombre]

            total_comprado = 0
            total_debe = 0

            for i, f in filas_cliente:
                cant = int(f[idx_cantidad]) if f[idx_cantidad] else 0
                prec = float(f[idx_precio]) if f[idx_precio] else 0
                total_v = cant * prec
                total_comprado += total_v
                if f[idx_estado] == "pendiente":
                    abonado_v = float(f[idx_abonado]) if idx_abonado is not None and len(f) > idx_abonado and f[idx_abonado] else 0
                    total_debe += (total_v - abonado_v)

            for i, f in filas_flores_cliente:
                cant = int(f[2]) if f[2] else 0
                prec = float(f[3]) if f[3] else 0
                total_v = cant * prec
                total_comprado += total_v
                if f[6] == "pendiente":
                    abonado_v = float(f[7]) if len(f) > 7 and f[7] else 0
                    total_debe += (total_v - abonado_v)

            with st.expander(f"{'🔴' if total_debe > 0 else '🟢'} {nombre} {'— ' + tel if tel else ''}"):
                col1, col2 = st.columns(2)
                col1.metric("Total comprado", f"${total_comprado:,.0f}")
                col2.metric("Debe", f"${total_debe:,.0f}")

                if filas_cliente:
                    st.markdown("**🌿 Compras de desodorante:**")
                    for i, f in filas_cliente:
                        fila_real = i + 2
                        cant = int(f[idx_cantidad]) if f[idx_cantidad] else 0
                        prec = float(f[idx_precio]) if f[idx_precio] else 0
                        total_v = cant * prec
                        abonado_v = float(f[idx_abonado]) if idx_abonado is not None and len(f) > idx_abonado and f[idx_abonado] else 0
                        saldo_v = total_v - abonado_v
                        estado_v = f[idx_estado]

                        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                        c1.write(f"{f[idx_fecha]} — {f[idx_producto]} ×{cant}")
                        c2.write(f"${total_v:,.0f}")
                        c3.write("🔴 Debe $" + f"{saldo_v:,.0f}" if estado_v == "pendiente" else "🟢 Pagado")

                        with c4.popover("⚙️"):
                            nuevo_estado = st.selectbox("Estado", ["pagado", "pendiente"], index=0 if estado_v == "pagado" else 1, key=f"est_{fila_real}")
                            nuevo_abonado = abonado_v
                            if nuevo_estado == "pendiente":
                                nuevo_abonado = st.number_input("Abonado ($)", min_value=0.0, max_value=float(total_v), value=float(abonado_v), step=1000.0, key=f"ab_{fila_real}")
                            else:
                                nuevo_abonado = total_v
                            cg, cb = st.columns(2)
                            if cg.button("💾", key=f"g_{fila_real}", use_container_width=True):
                                ventas_ws.update_cell(fila_real, idx_estado + 1, nuevo_estado)
                                if idx_abonado is not None:
                                    ventas_ws.update_cell(fila_real, idx_abonado + 1, nuevo_abonado)
                                st.success("Actualizado.")
                                st.rerun()
                            if cb.button("🗑️", key=f"b_{fila_real}", use_container_width=True):
                                actualizar_inventario(sheet, f[idx_producto], cant, datetime.now().strftime("%Y-%m-%d %H:%M"))
                                ventas_ws.delete_rows(fila_real)
                                st.success("Borrado.")
                                st.rerun()

                if filas_flores_cliente:
                    st.markdown("**🌸 Compras de flores:**")
                    for i, f in filas_flores_cliente:
                        fila_real_f = i + 2
                        cant = int(f[2]) if f[2] else 0
                        prec = float(f[3]) if f[3] else 0
                        total_v = cant * prec
                        abonado_v = float(f[7]) if len(f) > 7 and f[7] else 0
                        saldo_v = total_v - abonado_v
                        estado_v = f[6]
                        nota_v = f[8] if len(f) > 8 else ""

                        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                        c1.write(f"{f[0]} — {f[1]} ×{cant}" + (f" ({nota_v})" if nota_v else ""))
                        c2.write(f"${total_v:,.0f}")
                        c3.write("🔴 Debe $" + f"{saldo_v:,.0f}" if estado_v == "pendiente" else "🟢 Pagado")

                        with c4.popover("⚙️"):
                            nuevo_estado_f = st.selectbox("Estado", ["pagado", "pendiente"], index=0 if estado_v == "pagado" else 1, key=f"estf_{fila_real_f}")
                            nuevo_abonado_f = abonado_v
                            if nuevo_estado_f == "pendiente":
                                nuevo_abonado_f = st.number_input("Abonado ($)", min_value=0.0, max_value=float(total_v), value=float(abonado_v), step=1000.0, key=f"abf_{fila_real_f}")
                            else:
                                nuevo_abonado_f = total_v
                            cg2, cb2 = st.columns(2)
                            if cg2.button("💾", key=f"gf_{fila_real_f}", use_container_width=True):
                                ventas_flores_ws.update_cell(fila_real_f, 7, nuevo_estado_f)
                                ventas_flores_ws.update_cell(fila_real_f, 8, nuevo_abonado_f)
                                st.success("Actualizado.")
                                st.rerun()
                            if cb2.button("🗑️", key=f"bf_{fila_real_f}", use_container_width=True):
                                ventas_flores_ws.delete_rows(fila_real_f)
                                st.success("Borrado.")
                                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ⏳ PEDIDOS PENDIENTES
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "⏳ Pedidos Pendientes":
    st.title("⏳ Pedidos Pendientes")
    st.caption("Clientes que encargaron pero aún no se les ha entregado.")

    pedidos = get_pedidos(sheet)

    with st.expander("➕ Agregar pedido nuevo"):
        with st.form("form_pedido"):
            cliente_p = st.text_input("Nombre del cliente")
            producto_p = st.selectbox("Producto", PRODUCTOS + TIPOS_FLOR)
            cantidad_p = st.number_input("Cantidad", min_value=1, step=1)
            submitted_p = st.form_submit_button("Guardar pedido", use_container_width=True)

        if submitted_p:
            if not cliente_p:
                st.error("Escribí el nombre del cliente.")
            else:
                fecha_p = datetime.now().strftime("%Y-%m-%d %H:%M")
                sheet.worksheet("PEDIDOS_PENDIENTES").append_row([fecha_p, cliente_p, producto_p, int(cantidad_p)])
                st.success("✅ Pedido guardado.")
                st.rerun()

    st.markdown("---")

    if not pedidos:
        st.info("No hay pedidos pendientes.")
    else:
        pedidos_ws = sheet.worksheet("PEDIDOS_PENDIENTES")
        for i, pedido in enumerate(pedidos):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.write(f"**{pedido['cliente']}**")
            col2.write(f"{pedido['producto']}")
            col3.write(f"{pedido['cantidad']} unid.")
            if col4.button("✅", key=f"entregar_{i}", help="Marcar como entregado"):
                pedidos_ws.delete_rows(i + 2)
                st.success(f"Pedido de {pedido['cliente']} entregado. Registrá la venta.")
                st.rerun()