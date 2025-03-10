import schedule
import time
from fastapi import FastAPI
from .sync import sync_daily_data
from .config import settings
from .api.reports import router as reports_router
from .api.sync_api import router as sync_router
from .logging_config import logger

app = FastAPI()

app.include_router(reports_router, prefix="/api")
app.include_router(sync_router, prefix="/api")

@app.on_event("startup")
def schedule_sync():
    logger.info(f"Scheduling daily synchronization every {settings.sync_interval_minutes} minutes")
    schedule.every(settings.sync_interval_minutes).minutes.do(sync_daily_data)

    def run_scheduled_jobs():
        while True:
            schedule.run_pending()
            time.sleep(1)

    import threading
    thread = threading.Thread(target=run_scheduled_jobs, daemon=True)
    thread.start()

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down the application")