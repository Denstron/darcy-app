import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credenciales.json", scopes=SCOPES)
cliente = gspread.authorize(creds)
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1InoW_Xvb5KUGlvbJnOV6zaOAik706ZoV4FwSJIx-xzU/edit")

# COMPRAS — insertar encabezado en fila 1
compras = sheet.worksheet("COMPRAS")
compras.insert_row(["fecha", "producto", "cantidad", "precio_unitario", "gasto_envio"], index=1)

# VENTAS
ventas = sheet.worksheet("VENTAS")
ventas.insert_row(["fecha", "producto", "cantidad", "cliente", "estado_pago", "precio_unitario_venta"], index=1)

# CLIENTES
clientes = sheet.worksheet("CLIENTES")
clientes.insert_row(["nombre", "telefono"], index=1)

# PEDIDOS_PENDIENTES
pedidos = sheet.worksheet("PEDIDOS_PENDIENTES")
pedidos.insert_row(["fecha_pedido", "cliente", "producto", "cantidad"], index=1)

print("✅ Encabezados agregados correctamente")