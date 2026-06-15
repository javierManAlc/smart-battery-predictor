import duckdb
import polars as pl
from src.config import DATABASE_PATH


class FeatureBuilder:

    def __init__(self):
        self.db_path = DATABASE_PATH

    def run(self):
        """Une las tablas de precios y clima manteniendo la resolución

        de 15 minutos mediante un Left Join e imputación Forward Fill.
        """
        print(
            "🍳 [DATA MODELING] Cocinando el Tablón Maestro de Alta Resolución (15 min)..."
        )

        # 1. Nos conectamos a DuckDB para extraer las tablas a Polars
        conn = duckdb.connect(self.db_path)

        # Pasamos las tablas de DuckDB directamente a DataFrames de Polars
        df_prices = conn.execute("SELECT * FROM staging_prices").pl()
        df_weather = conn.execute("SELECT * FROM staging_weather").pl()

        conn.close()

        if df_prices.is_empty() or df_weather.is_empty():
            print("❌ Una de las tablas de staging está vacía. Abortando.")
            return

        # 2. LA MAGIA DEL TIME-SERIES: Left Join + Forward Fill
        # Aseguramos que el tiempo esté ordenado cronológicamente
        df_prices = df_prices.sort("timestamp")
        df_weather = df_weather.sort("timestamp")

        # Hacemos Left Join: Conservamos el 100% de los registros de precios
        df_joined = df_prices.join(df_weather, on="timestamp", how="left")

        # Rellenamos los 'nulls' del clima copiando el dato de la hora en punto hacia adelante
        df_master = df_joined.with_columns(
            [
                pl.col("temperature_c").forward_fill(),
                pl.col("solar_radiation_w_m2").forward_fill(),
            ]
        )

        print(
            f"⚡ Fusión e interpolación completadas con Polars ({df_master.height} filas)."
        )

        # 3. Guardamos el resultado final de vuelta en DuckDB
        conn = duckdb.connect(self.db_path)

        # Sobrescribimos la tabla analítica con el tablón de alta resolución
        conn.execute("CREATE OR REPLACE TABLE analytical_features AS SELECT * FROM df_master")
        
        total_rows = conn.execute(
            "SELECT COUNT(*) FROM analytical_features"
        ).fetchone()[0]
        conn.close()

        print(
            f"💾 Tablón Maestro de producción guardado. Total registros: {total_rows} (¡Sin perder cuartos de hora!)\n"
        )