import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credenciales.json", scopes=SCOPES)
cliente = gspread.authorize(creds)
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1InoW_Xvb5KUGlvbJnOV6zaOAik706ZoV4FwSJIx-xzU/edit")

ventas = sheet.worksheet("VENTAS")
headers = ventas.row_values(1)

if "abonado" not in headers:
    # Agregar encabezado en la siguiente columna libre
    col_nueva = len(headers) + 1
    ventas.update_cell(1, col_nueva, "abonado")

    # Para las filas existentes: si estado_pago es "pagado", abonado = precio*cantidad. Si "pendiente", abonado = 0
    todas = ventas.get_all_values()
    idx_cantidad = headers.index("cantidad")
    idx_estado = headers.index("estado_pago")
    idx_precio = headers.index("precio_unitario_venta")

    for i, fila in enumerate(todas[1:], start=2):
        if len(fila) > idx_estado:
            cantidad = int(fila[idx_cantidad]) if fila[idx_cantidad] else 0
            precio = float(fila[idx_precio]) if fila[idx_precio] else 0
            total = cantidad * precio
            abonado = total if fila[idx_estado] == "pagado" else 0
            ventas.update_cell(i, col_nueva, abonado)

    print("✅ Columna 'abonado' agregada y completada para filas existentes")
else:
    print("ℹ️ La columna 'abonado' ya existe, no se hizo nada")