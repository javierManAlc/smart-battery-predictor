import polars as pl
import datetime
import duckdb
from src.ingestion.weather_client import WeatherClient
from src.config import DATABASE_PATH

class WeatherLoader:

    def __init__(self):
        self.client = WeatherClient()
        self.db_path = DATABASE_PATH

    def _init_db(self):
        """Inicializa la tabla del clima en DuckDB si no existe."""
        conn = duckdb.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS staging_weather (
                timestamp TIMESTAMP UNIQUE,
                temperature_c DOUBLE,
                solar_radiation_w_m2 DOUBLE
            )
        """
        )
        conn.close()

    def run(self, start_date: datetime.date, end_date: datetime.date):
        """Ejecuta el pipeline completo: Extraer, Transformar y Cargar"""
        # 1. Inicializar la base de datos
        self._init_db()

        # 2. EXTRAER: Obtener datos crudos (Lista de diccionarios)
        raw_data = self.client.fetch_weather(start_date, end_date)
        if not raw_data:
            print("❌ No se obtuvieron datos para cargar.")
            return
        
        # 3. TRANSFORMAR: Usar Polars para estructurar, limpiar y tipar
        # Convertimos la lista de dicts a un DataFrame de Polars
        df_raw = pl.DataFrame(raw_data)

        # Limpiamos: parseamos la fecha de string a Timestamp y renombramos columnas
        df_clean = df_raw.select(
            [
                pl.col("datetime")
                .str.strptime(pl.Datetime, format = "%Y-%m-%dT%H:%M")
                .alias("timestamp"),
                pl.col("temperature_c").cast(pl.Float64),
                pl.col("solar_radiation_w_m2").cast(pl.Float64)
            ]
        )

        print(f"⚡ Clima procesado con Polars ({df_clean.height} filas).")

        # 4. CARGAR: Insertar en DuckDB de manera inteligente (Upsert)
        conn = duckdb.connect(self.db_path)

        conn.execute(
            """
            INSERT OR IGNORE INTO staging_weather 
            SELECT timestamp, temperature_c, solar_radiation_w_m2 FROM df_clean
        """
        )

        total_rows = conn.execute(
            "SELECT COUNT(*) FROM staging_weather"
        ).fetchone()[0]

        conn.close()

        print(
            f"💾 Carga completada con éxito. Total registros en DuckDB: {total_rows}\n"
        )
