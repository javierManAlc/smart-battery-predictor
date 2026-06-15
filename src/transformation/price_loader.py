import datetime
import duckdb
import polars as pl
from src.config import DATABASE_PATH
from src.ingestion.esios_client import EsiosClient

class PriceLoader:

    def __init__(self):
        self.client = EsiosClient()
        self.db_path = DATABASE_PATH

    def _init_db(self):
        """Inicializa la tabla en DuckDB si no existe."""
        conn = duckdb.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS staging_prices (
                timestamp TIMESTAMP UNIQUE,
                price_eur_mwh DOUBLE
            )
        """
        )
        conn.close()

    def run(self, start_date: datetime.date, end_date: datetime.date):
        """Ejecuta el pipeline completo: Extraer, Transformar y Cargar"""
        # 1. Inicializar la base de datos
        self._init_db()

        # 2. EXTRAER: Obtener datos crudos (Lista de diccionarios)
        raw_data = self.client.fetch_prices(start_date, end_date)
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
                .str.strptime(pl.Datetime, format = "%Y-%m-%dT%H:%M:%S%.3f%z")
                .dt.replace_time_zone(None) # Quitamos zona horaria para DuckDB
                .alias("timestamp"),
                pl.col("value").cast(pl.Float64).alias("price_eur_mwh"),
            ]
        )

        print(f"⚡ Datos procesados con Polars ({df_clean.height} filas).")

        # 4. CARGAR: Insertar en DuckDB de manera inteligente (Upsert)
        conn = duckdb.connect(self.db_path)

        conn.execute(
            """
            INSERT OR IGNORE INTO staging_prices 
            SELECT timestamp, price_eur_mwh FROM df_clean
        """
        )

        total_rows = conn.execute(
            "SELECT COUNT(*) FROM staging_prices"
        ).fetchone()[0]

        conn.close()

        print(
            f"💾 Carga completada con éxito. Total registros en DuckDB: {total_rows}\n"
        )