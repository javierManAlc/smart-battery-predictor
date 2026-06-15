import datetime
from src.ingestion.weather_client import WeatherClient

client = WeatherClient()
hoy = datetime.date.today()
hace_tres_dias = hoy - datetime.timedelta(days=15)
fin_seguro = hoy - datetime.timedelta(days=5)

datos_clima = client.fetch_weather(start_date=hace_tres_dias, end_date=fin_seguro)

if datos_clima:
    print(
        f"✅ ¡Éxito! Hemos recuperado {len(datos_clima)} horas de datos climáticos reales."
    )
    print("Muestra de las primeras horas:")
    for fila in datos_clima[:3]:
        print(
            f" - Hora: {fila['datetime']} | Temp: {fila['temperature_c']}°C | Radiación: {fila['solar_radiation_w_m2']} W/m²"
        )