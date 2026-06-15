import datetime
from src.ingestion.esios_client import EsiosClient

# Inicializamos el cliente. Ahora leerá tu token real.
client = EsiosClient()

# Vamos a pedir los datos de ayer y hoy
hoy = datetime.date.today()
ayer = hoy - datetime.timedelta(days = 1)


print("🔌 Conectando con Red Eléctrica de España...")
precios_reales = client.fetch_prices(start_date = ayer, end_date = hoy)

if precios_reales:
    print(f"✅ ¡Conexión exitosa! Hemos recibido {len(precios_reales)} registros reales.")
    print("\nAquí tienes una muestra de los precios reales del mercado spot español:")
    for p in precios_reales[:5]:
        print(f" - Fecha: {p['datetime']} | Precio Real: {p['value']} €/MWh")
else:
    print("❌ Algo falló. No hemos recibido datos. Revisa si copiaste bien el token.")