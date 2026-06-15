import datetime
from dagster import asset
from src.transformation.price_loader import PriceLoader
from src.transformation.weather_loader import WeatherLoader
from src.transformation.feature_builder import FeatureBuilder


@asset
def staging_prices():
    """Activo que descarga los precios reales de la luz desde ESIOS

    y los almacena en DuckDB.
    """
    loader = PriceLoader()
    hoy = datetime.date.today()
    hace_un_dia = hoy - datetime.timedelta(days=1)

    print("🔌 [Dagster] Lanzando ingesta de precios...")
    loader.run(start_date=hace_un_dia, end_date=hoy)


@asset(deps=[staging_prices])
def staging_weather():
    """Activo que descarga el clima real de Sevilla desde Open-Meteo

    y lo almacena en DuckDB.
    """
    loader = WeatherLoader()
    hoy = datetime.date.today()
    hace_un_dia = hoy - datetime.timedelta(days=1)

    print("🌞 [Dagster] Lanzando ingesta de clima...")
    loader.run(start_date=hace_un_dia, end_date=hoy)


@asset(deps=[staging_prices, staging_weather])
def analytical_features():
    """Activo que fusiona los precios y el clima en el Tablón Maestro

    una vez que las ingestas previas han terminado con éxito.
    """
    builder = FeatureBuilder()
    print("🍳 [Dagster] Cocinando el Tablón Maestro de Alta Resolución...")
    builder.run()