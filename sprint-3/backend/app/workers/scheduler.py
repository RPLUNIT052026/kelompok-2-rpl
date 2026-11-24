from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.services.aggregator import DataAggregator

settings = get_settings()
scheduler = AsyncIOScheduler(timezone="UTC")


async def run_aggregator_cycle() -> None:
    db: Session = SessionLocal()
    try:
        await DataAggregator(db, redis_client).run_cycle()
    finally:
        db.close()


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        run_aggregator_cycle,
        trigger="interval",
        seconds=settings.fetch_interval_seconds,
        id="data_aggregator",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
