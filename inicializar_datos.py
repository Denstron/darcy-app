import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credenciales.json", scopes=SCOPES)
cliente = gspread.authorize(creds)
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1InoW_Xvb5KUGlvbJnOV6zaOAik706ZoV4FwSJIx-xzU/edit")

# INVENTARIO
inv = sheet.worksheet("INVENTARIO")
inv.clear()
inv.append_row(["producto", "cantidad", "ultima_actualizacion"])
inv.append_row(["Tarro mediano", 0, ""])
inv.append_row(["Tarrito spray", 7, ""])

# CONFIG
cfg = sheet.worksheet("CONFIG")
cfg.clear()
cfg.append_row(["clave", "valor"])
cfg.append_row(["costo_tarro_mediano", 10200])
cfg.append_row(["precio_tarro_mediano", 20000])
cfg.append_row(["costo_tarrito_spray", 1800])
cfg.append_row(["precio_tarrito_spray", 3000])
cfg.append_row(["porcentaje_reinversion", 60])

print("✅ Datos iniciales cargados correctamente")