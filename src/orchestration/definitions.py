from dagster import Definitions, load_assets_from_modules, define_asset_job, ScheduleDefinition
from src.orchestration import assets

all_assets = load_assets_from_modules([assets])

pipeline_job = define_asset_job(
    name="actualizar_todo_el_pipeline",
    selection = "*"
)

daily_schedule = ScheduleDefinition(
    name = "alarma_diaria_madrugada",
    cron_schedule = "0 3 * * *",
    job = pipeline_job,
    execution_timezone="Europe/Madrid"
)

defs = Definitions(
    assets=all_assets,
    jobs=[pipeline_job],
    schedules=[daily_schedule]
)