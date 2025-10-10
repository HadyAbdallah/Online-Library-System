# app/celery_app.py
from celery import Celery
from app.config import settings

# This creates the Celery instance that other modules can import
celery_app = Celery(
    'tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)