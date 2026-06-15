import numpy
import duckdb
from src.config import DATABASE_PATH

# Nos conectamos en modo lectura
conn = duckdb.connect(DATABASE_PATH, read_only=True)
conn.execute("SET max_temp_directory_size = 10000;") 

print("📊 TABLAS DISPONIBLES EN EL DATA WAREHOUSE:")
# .df() hace que DuckDB nos muestre el resultado formateado como una tabla limpia
print(conn.execute("SHOW TABLES").df())

print("\n🌞 MUESTRA DE LA TABLA DE CLIMA (analytical_features):")
conn.sql("SELECT * FROM analytical_features LIMIT 100").show()

conn.close()