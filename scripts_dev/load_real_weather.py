import datetime
from src.transformation.weather_loader import WeatherLoader

if __name__ == "__main__":
    loader = WeatherLoader()
    
    hoy = datetime.date.today()
    # Nos traemos las últimas dos semanas de datos reales
    hace_seis_meses = hoy - datetime.timedelta(days=180)
    
    print("🚀 Lanzando pipeline con datos REALES del mercado spot...")
    loader.run(start_date=hace_seis_meses, end_date=hoy)
    print("🏁 ¡Proceso completado! Tus datos reales ya están a buen recaudo.")