import datetime
import math
import random
import requests
from src.config import ESIOS_TOKEN, ESIOS_BASE_URL


class EsiosClient:

    def __init__(self):
        self.token = ESIOS_TOKEN
        self.base_url = ESIOS_BASE_URL
        # Usaremos el indicador 10234 (Precio de mercado diario spot en España)
        self.indicator_id = "10234"

    def _generate_mock_data(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> list[dict]:
        """Genera datos falsos con la estructura exacta de ESIOS,

        simulando el efecto de canibalización solar (precios bajos a mediodía).
        """
        mock_values = []
        current_date = start_date

        while current_date <= end_date:
            for hour in range(24):
                # Crear un timestamp simulado con zona horaria de España
                dt = datetime.datetime.combine(
                    current_date, datetime.time(hour=hour)
                )
                dt_iso = dt.strftime("%Y-%m-%dT%H:00:00.000+02:00")

                # --- EFECTO CANIBALIZACIÓN SOLAR (Curva de Pato) ---
                # Por la noche/mañana el precio base es alto (70-100 €/MWh)
                # A mitad del día (11:00 a 16:00) el precio cae drásticamente por el sol
                if 11 <= hour <= 16:
                    base_price = random.uniform(
                        0.0, 15.0
                    )  # ¡Casi gratis a mitad del día!
                elif 19 <= hour <= 22:
                    base_price = random.uniform(
                        110.0, 150.0
                    )  # Pico nocturno caro
                else:
                    base_price = random.uniform(60.0, 85.0)  # Resto del día

                # Añadir un componente senoidal suave para que parezca más real
                noise = math.sin(hour / 24 * math.pi * 2) * 5
                final_price = max(0.0, round(base_price + noise, 2))

                # Estructura de diccionario idéntica al JSON que devuelve ESIOS
                mock_values.append({"value": final_price, "datetime": dt_iso})

            current_date += datetime.timedelta(days=1)

        return {"indicator": {"name": "Precio mercado diario", "values": mock_values}}

    def fetch_prices(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> list[dict]:
        """Obtiene los precios de la luz. Si el token es el de prueba,

        devuelve datos simulados automáticos.
        """
        # Si no tenemos token real, usamos el simulador senior
        if not self.token or "temporal_o_real" in self.token:
            print(
                f"🤖 [MOCK MODE] Generando datos simulados desde {start_date} hasta {end_date}..."
            )
            data = self._generate_mock_data(start_date, end_date)
            return data["indicator"]["values"]

        # --- CÓDIGO REAL PARA CUANDO TENGAS EL TOKEN ---
        print(
            f"🌐 [API MODE] Conectando a ESIOS para fechas: {start_date} a {end_date}..."
        )
        url = f"{self.base_url}/{self.indicator_id}"
        headers = {
            "Accept": "application/json; application/vnd.esios-api-v1+json",
            "Content-Type": "application/json",
            "Host": "api.esios.ree.es",
            "x-api-key": self.token,
        }
        params = {
            "start_date": f"{start_date}T00:00:00",
            "end_date": f"{end_date}T23:59:59",
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            res_json = response.json()
            return res_json["indicator"]["values"]
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al conectar con la API de ESIOS: {e}")
            return []