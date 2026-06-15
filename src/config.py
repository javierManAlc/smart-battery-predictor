import os
from pathlib import Path
from dotenv import load_dotenv

# Localizar la raíz del proyecto y cargar el archivo .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Variables globales que usará nuestro pipeline
ESIOS_TOKEN = os.getenv("ESIOS_API_TOKEN")
ESIOS_BASE_URL = os.getenv("ESIOS_BASE_URL")
DATABASE_PATH = str(BASE_DIR / "data" / "database" / "warehouse.db")

# Validación simple de seguridad
if not ESIOS_TOKEN or ESIOS_TOKEN == "tu_token_temporal_o_real":
    print("⚠️  Aviso: ESIOS_API_TOKEN no configurado correctamente en el archivo .env")