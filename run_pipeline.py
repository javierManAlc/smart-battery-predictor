import datetime
from src.transformation.price_loader import PriceLoader

if __name__ == "__main__":
    loader = PriceLoader()

    # Vamos a cargar datos simulados de los últimos 7 días
    fin = datetime.date.today()
    inicio = fin - datetime.timedelta(days=7)

    print("🚀 Iniciando pipeline de ingeniería de datos...")
    loader.run(start_date=inicio, end_date=fin)
    print("🏁 Pipeline finalizado.")