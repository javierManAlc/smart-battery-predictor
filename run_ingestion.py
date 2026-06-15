import datetime
from src.ingestion.esios_client import EsiosClient

# Inicializamos nuestro cliente
client = EsiosClient()

# Definimos un rango de fechas de prueba (los últimos 2 días)
hoy = datetime.date.today()
hace_dos_dias = hoy - datetime.timedelta(days=2)

# Recuperamos los datos
precios = client.fetch_prices(start_date=hace_dos_dias, end_date=hoy)

# Mostramos los primeros 3 registros para validar el formato
print(f"\nSe han descargado {len(precios)} registros horarios.")
print("Muestra de los primeros datos:")
for p in precios[:5]:
    print(f" - Fecha/Hora: {p['datetime']} | Precio: {p['value']} €/MWh")