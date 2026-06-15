import polars
import duckdb
from src.transformation.feature_builder import FeatureBuilder


if __name__ == "__main__":
    builder = FeatureBuilder()
    builder.run()

    conn = duckdb.connect(builder.db_path, read_only=True)
    print("\n👀 AQUÍ TIENES UNA MUESTRA DEL TABLÓN MAESTRO (analytical_features):")
    print(conn.execute("SELECT * FROM analytical_features").pl())
    conn.close()
