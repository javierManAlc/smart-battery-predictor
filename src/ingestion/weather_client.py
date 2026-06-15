import datetime
import requests

class WeatherClient:

    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        self.latitude = 37.3828
        self.longitude = -5.9731

    def fetch_weather(self, start_date: datetime.date, end_date: datetime.date) -> list[dict]:
        """
        Conecta con Open-Meteo y extrae la temperatura y la radiación solar horaria para las coordenadas de la planta
        """
        print(
            f"🌞 [API WEATHER] Extrayendo clima real para Sevilla (Lat: {self.latitude}, Lon: {self.longitude})..."
        )

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "hourly": "temperature_2m,shortwave_radiation",
            "timezone": "Europe/Madrid",
        }
        try:
            response = requests.get(self.base_url, params = params)
            response.raise_for_status()
            data = response.json()

            hourly_data = data.get("hourly",{})
            timestamps = hourly_data.get("time", [])
            temperatures = hourly_data.get("temperature_2m", [])
            radiation = hourly_data.get("shortwave_radiation", [])

            records = []
            for i in range(len(timestamps)):
                records.append(
                    {
                        "datetime": timestamps[i],
                        "temperature_c": temperatures[i],
                        "solar_radiation_w_m2": radiation[i],
                    }
                )

            return records
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al conectar con la API de Open-Meteo: {e}")
            return []