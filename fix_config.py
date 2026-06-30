import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credenciales.json", scopes=SCOPES)
cliente = gspread.authorize(creds)
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1InoW_Xvb5KUGlvbJnOV6zaOAik706ZoV4FwSJIx-xzU/edit")

# ── Actualizar CONFIG con todos los productos correctos ──
cfg = sheet.worksheet("CONFIG")
cfg.clear()
cfg.append_row(["clave", "valor"])
cfg.append_row(["costo_tarro_mediano", 10200])
cfg.append_row(["precio_tarro_mediano", 20000])
cfg.append_row(["costo_tarrito_spray_vacio", 1800])
cfg.append_row(["precio_tarrito_spray_vacio", 2000])
cfg.append_row(["costo_tarrito_spray_lleno", 1800])
cfg.append_row(["precio_tarrito_spray_lleno", 15000])
cfg.append_row(["porcentaje_reinversion", 60])

# ── Actualizar INVENTARIO con el nuevo producto ──
inv = sheet.worksheet("INVENTARIO")
inv_data = inv.get_all_records()
nombres_actuales = [row["producto"] for row in inv_data]

if "Tarrito spray" in nombres_actuales:
    # renombrar "Tarrito spray" -> "Tarrito spray vacío" si existe
    for i, row in enumerate(inv_data):
        if row["producto"] == "Tarrito spray":
            inv.update_cell(i + 2, 1, "Tarrito spray vacío")
            break

if "Tarrito spray lleno" not in [r["producto"] for r in inv.get_all_records()]:
    inv.append_row(["Tarrito spray lleno", 0, ""])

print("✅ CONFIG e INVENTARIO actualizados correctamente")