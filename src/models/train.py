import polars as pl
import duckdb
from src.config import DATABASE_PATH
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

class PricePredictor:
    def __init__(self):
        self.db_path = DATABASE_PATH

    def extract_and_engineer_features(self) -> pl.DataFrame:
        """Extrae los datos de DuckDB y aplica ingeniería de

        características temporales robustas mediante Joins de Polars.
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        df = conn.execute("SELECT * FROM analytical_features").pl()
        conn.close()

        # 1. Aseguramos que el timestamp sea de tipo Fecha/Hora nativo
        df = df.with_columns(pl.col("timestamp").cast(pl.Datetime))

        print("🧬 Fabricando características de calendario...")
        df_base = df.with_columns(
            [
                pl.col("timestamp").dt.hour().alias("feature_hour"),
                pl.col("timestamp").dt.weekday().alias("feature_day_of_week"),
            ]
        )

        print("🚀 Construyendo máquina del tiempo matemática (Temporal Joins)...")

        # Creamos un dataframe gemelo para el Lag de 24 horas
        # Le sumamos 24 horas a su tiempo. Al cruzarlo, el precio del pasado se alineará con el presente.
        df_lag_24 = df.select(["timestamp", "price_eur_mwh"]).with_columns(
            (pl.col("timestamp") + pl.duration(days=1)).alias("timestamp")
        ).rename({"price_eur_mwh": "feature_price_lag_24h"})

        # Creamos otro gemelo para el Lag de 48 horas (2 días al pasado)
        df_lag_48 = df.select(["timestamp", "price_eur_mwh"]).with_columns(
            (pl.col("timestamp") + pl.duration(days=2)).alias("timestamp")
        ).rename({"price_eur_mwh": "feature_price_lag_48h"})

        # Fusionamos los gemelos con nuestro dataframe base usando la fecha exacta
        df_features = (
            df_base.join(df_lag_24, on="timestamp", how="left")
            .join(df_lag_48, on="timestamp", how="left")
        )

        # Añadimos la ventana móvil del clima (esta sí puede ir por filas si está ordenada)
        df_features = df_features.sort("timestamp").with_columns(
            pl.col("solar_radiation_w_m2")
            .rolling_mean(window_size=16)
            .alias("feature_solar_rolling_mean_4h")
        )

        return df_features.drop_nulls()
    
    def train(self):
        """Prepara las matrices, entrena el XGBoost y evalúa el error."""

        df = self.extract_and_engineer_features()

        feature_cols = [c for c in df.columns if c.startswith("feature_")]
        target_col = "price_eur_mwh"

        X = df.select(feature_cols).to_pandas()
        y = df.select(target_col).to_pandas()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        print(
            f"🏋️ Entrenando XGBoost con {len(X_train)} filas de entrenamiento y {len(X_test)} de test..."
        )

        model = XGBRegressor(n_estimators=100, learning_rate=0.05, random_state=42)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)

        print("\n📊 RESULTADOS DEL MODELO:")
        print(
            f"🎯 Error Medio Absoluto (MAE): {mae:.2f} EUR/MWh"
        )
        print(
            f"💡 Significado: De media, el modelo se equivoca por solo {mae:.2f}€ en cada cuarto de hora.\n"
        )

if __name__ == "__main__":
    predictor = PricePredictor()
    predictor.train()