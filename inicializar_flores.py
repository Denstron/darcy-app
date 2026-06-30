import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credenciales.json", scopes=SCOPES)
cliente = gspread.authorize(creds)
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1InoW_Xvb5KUGlvbJnOV6zaOAik706ZoV4FwSJIx-xzU/edit")

# VENTAS_FLORES
try:
    sheet.add_worksheet(title="VENTAS_FLORES", rows=500, cols=10)
except:
    pass
vf = sheet.worksheet("VENTAS_FLORES")
vf.clear()
vf.append_row(["fecha", "tipo_flor", "cantidad", "precio_unitario", "costo_unitario", "cliente", "estado_pago", "abonado", "nota"])

# COMPRAS_FLORES (materiales)
try:
    sheet.add_worksheet(title="COMPRAS_FLORES", rows=500, cols=6)
except:
    pass
cf = sheet.worksheet("COMPRAS_FLORES")
cf.clear()
cf.append_row(["fecha", "material", "cantidad", "precio_unitario", "total"])

# CONFIG_FLORES
try:
    sheet.add_worksheet(title="CONFIG_FLORES", rows=50, cols=2)
except:
    pass
cfg = sheet.worksheet("CONFIG_FLORES")
cfg.clear()
cfg.append_row(["clave", "valor"])
cfg.append_row(["precio_flor_grande", 50000])
cfg.append_row(["costo_flor_grande", 30000])
cfg.append_row(["precio_flor_mediana", 35000])
cfg.append_row(["costo_flor_mediana", 21000])
cfg.append_row(["precio_flor_pequena", 20000])
cfg.append_row(["costo_flor_pequena", 13000])
cfg.append_row(["precio_flor_pedido", 0])
cfg.append_row(["costo_flor_pedido", 0])
cfg.append_row(["porcentaje_reinversion_flores", 60])

print("✅ Pestañas de flores creadas correctamente")