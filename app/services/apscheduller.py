from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

import logging
from app import config

jobstores = {
    'default': RedisJobStore(
        jobs_key="curChange.jobs",
        run_times_key="curChange.run_times",
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB
    )
}
executors = {'default': AsyncIOExecutor()}
job_defaults = {
    'coalesce': False,
    'max_instances': 20,
    'misfire_grace_time': 3600
}
logger.info("configuring scheduler...")
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    job_defaults=job_defaults,
    executors=executors
)
apshl = logging.getLogger('apscheduler')
apshl.setLevel(logging.INFO)
apshl.addHandler(
    logging.FileHandler(
        config.app_dir / 'log' / f'apshe_{config.PRINT_LOG}'
    )
)


async def on_startup(dispatcher: Dispatcher):
    logger.info("starting scheduler...")
    scheduler.start()


async def on_shutdown(dispatcher: Dispatcher):
    scheduler.shutdown()


def setup(executor: Executor):
    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)
