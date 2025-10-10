# celery_worker.py
from app import create_app
from app.celery_app import celery_app

# Create the Flask app
flask_app = create_app()

# Update the Celery app's configuration with the Flask app's config
celery_app.conf.update(flask_app.config)