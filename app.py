import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import base64

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
    [data-testid="stAppViewContainer"] { background-color: #fff8f9; }
    [data-testid="stSidebar"] { background-color: #fce4ec; }
    [data-testid="stSidebar"] * { color: #880e4f !important; }
    h1, h2, h3 { color: #c2185b !important; }
    p, span, div, label { color: #333333 !important; }
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
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #f8bbd0;
        box-shadow: 0 2px 8px rgba(233,30,140,0.08);
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label { color: #880e4f !important; font-weight: 600 !important; }
    [data-testid="stSuccess"] { background-color: #e8f5e9 !important; }
    [data-testid="stInfo"] { background-color: #fce4ec !important; }
    .stRadio label { color: #880e4f !important; font-weight: 500 !important; }
    .stExpander { border: 1px solid #f8bbd0 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Login ──────────────────────────────────────────────────────────────────────
def check_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

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
            "Denstron": "danieL0105",
            "Darcy": "Darcy0105"
        }

        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")

        if st.button("Entrar", use_container_width=True):
            if usuario in USUARIOS and clave == USUARIOS[usuario]:
                st.session_state.autenticado = True
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

def get_config(sheet):
    cfg = sheet.worksheet("CONFIG").get_all_records()
    return {row["clave"]: float(row["valor"]) for row in cfg}

def get_inventario(sheet):
    return sheet.worksheet("INVENTARIO").get_all_records()

def get_ventas(sheet):
    return sheet.worksheet("VENTAS").get_all_records()

def get_compras(sheet):
    return sheet.worksheet("COMPRAS").get_all_records()

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

st.sidebar.markdown("---")

menu = st.sidebar.radio("Menú", [
    "📊 Dashboard",
    "📦 Inventario",
    "🛒 Registrar Compra",
    "💰 Registrar Venta",
    "👥 Clientes",
    "⏳ Pedidos Pendientes"
])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.autenticado = False
    st.rerun()

PRODUCTOS = ["Tarro mediano", "Tarrito spray"]

# ══════════════════════════════════════════════════════════════════════════════
# 📊 DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if menu == "📊 Dashboard":
    st.title("📊 Panel de Control")

    config = get_config(sheet)
    ventas = get_ventas(sheet)
    compras = get_compras(sheet)
    inventario = get_inventario(sheet)

    precios_costo = {
        "Tarro mediano": config["costo_tarro_mediano"],
        "Tarrito spray": config["costo_tarrito_spray"]
    }

    total_vendido = 0
    total_ganancia = 0
    total_pendiente = 0

    for v in ventas:
        cantidad = int(v["cantidad"])
        precio = float(v["precio_unitario_venta"])
        producto = v["producto"]
        ingreso = cantidad * precio
        total_vendido += ingreso
        if v["estado_pago"] == "pendiente":
            total_pendiente += ingreso
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
        st.subheader("📋 Últimas ventas")
        df_show = df_ventas[["fecha", "producto", "cantidad", "cliente", "estado_pago", "precio_unitario_venta"]].copy()
        df_show.columns = ["Fecha", "Producto", "Cantidad", "Cliente", "Estado", "Precio unit."]
        st.dataframe(df_show.tail(10).iloc[::-1], use_container_width=True)
    else:
        st.info("Aún no hay ventas registradas.")

# ══════════════════════════════════════════════════════════════════════════════
# 📦 INVENTARIO
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📦 Inventario":
    st.title("📦 Inventario")
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
    st.subheader("Detalle completo")
    df = pd.DataFrame(inventario)
    st.dataframe(df, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 🛒 REGISTRAR COMPRA
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "🛒 Registrar Compra":
    st.title("🛒 Registrar Compra")
    st.caption("Cada vez que comprás desde Montería, registrá acá.")

    config = get_config(sheet)

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
        **Resumen de esta compra:**
        - Producto: {producto}
        - Cantidad: {int(cantidad)} unidades
        - Inversión total: ${costo_total:,.0f}
        - Costo real por unidad (con envío): ${costo_real_unitario:,.0f}
        """)

# ══════════════════════════════════════════════════════════════════════════════
# 💰 REGISTRAR VENTA
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "💰 Registrar Venta":
    st.title("💰 Registrar Venta")

    config = get_config(sheet)
    inventario = get_inventario(sheet)
    inv_dict = {item["producto"]: int(item["cantidad"]) for item in inventario}

    precios_venta = {
        "Tarro mediano": config["precio_tarro_mediano"],
        "Tarrito spray": config["precio_tarrito_spray"]
    }
    precios_costo = {
        "Tarro mediano": config["costo_tarro_mediano"],
        "Tarrito spray": config["costo_tarrito_spray"]
    }

    with st.form("form_venta"):
        cliente = st.text_input("Nombre del cliente")
        telefono = st.text_input("Teléfono (opcional)")
        producto = st.selectbox("Producto", PRODUCTOS)
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        estado_pago = st.selectbox("Estado del pago", ["pagado", "pendiente"])
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

            sheet.worksheet("VENTAS").append_row([fecha, producto, int(cantidad), cliente, estado_pago, precio_unit])
            actualizar_inventario(sheet, producto, -int(cantidad), fecha)
            registrar_cliente_si_nuevo(sheet, cliente, telefono)

            st.success("✅ Venta registrada")
            st.info(f"""
            **Resumen:**
            - Cliente: {cliente}
            - Producto: {producto} × {int(cantidad)}
            - Total cobrado: ${precio_unit * cantidad:,.0f}
            - Ganancia de esta venta: ${ganancia:,.0f}
            - Estado: {estado_pago}
            """)

# ══════════════════════════════════════════════════════════════════════════════
# 👥 CLIENTES
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "👥 Clientes":
    st.title("👥 Clientes")

    clientes = get_clientes(sheet)
    ventas = get_ventas(sheet)

    if not clientes:
        st.info("Aún no hay clientes registrados.")
    else:
        df_ventas = pd.DataFrame(ventas) if ventas else pd.DataFrame(
            columns=["fecha", "producto", "cantidad", "cliente", "estado_pago", "precio_unitario_venta"]
        )

        for cliente in clientes:
            nombre = cliente["nombre"]
            tel = cliente.get("telefono", "")

            if not df_ventas.empty:
                ventas_cliente = df_ventas[df_ventas["cliente"] == nombre].copy()
                ventas_cliente["cantidad"] = ventas_cliente["cantidad"].astype(int)
                ventas_cliente["precio_unitario_venta"] = ventas_cliente["precio_unitario_venta"].astype(float)
                ventas_cliente["total"] = ventas_cliente["cantidad"] * ventas_cliente["precio_unitario_venta"]
                total_comprado = ventas_cliente["total"].sum()
                pendiente = ventas_cliente[ventas_cliente["estado_pago"] == "pendiente"]["total"].sum()
            else:
                total_comprado = 0
                pendiente = 0

            with st.expander(f"{'🔴' if pendiente > 0 else '🟢'} {nombre} {'— ' + tel if tel else ''}"):
                col1, col2 = st.columns(2)
                col1.metric("Total comprado", f"${total_comprado:,.0f}")
                col2.metric("Debe", f"${pendiente:,.0f}")

                if not df_ventas.empty and not ventas_cliente.empty:
                    st.dataframe(
                        ventas_cliente[["fecha", "producto", "cantidad", "estado_pago", "total"]].rename(
                            columns={"fecha": "Fecha", "producto": "Producto", "cantidad": "Cantidad",
                                     "estado_pago": "Estado", "total": "Total ($)"}
                        ),
                        use_container_width=True
                    )

                pendientes_cliente = ventas_cliente[ventas_cliente["estado_pago"] == "pendiente"] if not df_ventas.empty and not ventas_cliente.empty else pd.DataFrame()
                if not pendientes_cliente.empty:
                    if st.button(f"✅ Marcar todo como pagado — {nombre}", key=f"pagar_{nombre}"):
                        ventas_ws = sheet.worksheet("VENTAS")
                        todas_ventas = ventas_ws.get_all_values()
                        for idx, fila in enumerate(todas_ventas):
                            if len(fila) >= 5 and fila[3] == nombre and fila[4] == "pendiente":
                                ventas_ws.update_cell(idx + 1, 5, "pagado")
                        st.success(f"✅ Pagos de {nombre} actualizados.")
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
            producto_p = st.selectbox("Producto", PRODUCTOS)
            cantidad_p = st.number_input("Cantidad", min_value=1, step=1)
            submitted_p = st.form_submit_button("Guardar pedido", use_container_width=True)

        if submitted_p:
            if not cliente_p:
                st.error("Escribí el nombre del cliente.")
            else:
                fecha_p = datetime.now().strftime("%Y-%m-%d %H:%M")
                sheet.worksheet("PEDIDOS_PENDIENTES").append_row(
                    [fecha_p, cliente_p, producto_p, int(cantidad_p)]
                )
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
                st.success(f"Pedido de {pedido['cliente']} entregado. Registrá la venta en 💰 Registrar Venta.")
                st.rerun()