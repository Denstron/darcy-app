import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credenciales.json", scopes=SCOPES)
cliente = gspread.authorize(creds)
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1InoW_Xvb5KUGlvbJnOV6zaOAik706ZoV4FwSJIx-xzU/edit")

# ── Actualizar INVENTARIO ──
inv = sheet.worksheet("INVENTARIO")
inv.clear()
inv.append_row(["producto", "cantidad", "ultima_actualizacion"])
inv.append_row(["Tarro 125ml", 12, ""])
inv.append_row(["Tarro 250ml", 12, ""])
inv.append_row(["Tarrito spray vacío", 0, ""])
inv.append_row(["Tarrito spray lleno", 0, ""])

# ── Actualizar CONFIG ──
cfg = sheet.worksheet("CONFIG")
cfg.clear()
cfg.append_row(["clave", "valor"])
cfg.append_row(["costo_tarro_125ml", 10200])
cfg.append_row(["precio_tarro_125ml", 20000])
cfg.append_row(["costo_tarro_250ml", 17700])
cfg.append_row(["precio_tarro_250ml", 35000])
cfg.append_row(["costo_tarrito_spray_vacio", 1800])
cfg.append_row(["precio_tarrito_spray_vacio", 2000])
cfg.append_row(["costo_tarrito_spray_lleno", 1800])
cfg.append_row(["precio_tarrito_spray_lleno", 15000])
cfg.append_row(["porcentaje_reinversion", 60])

print("✅ Inventario y precios actualizados correctamente")