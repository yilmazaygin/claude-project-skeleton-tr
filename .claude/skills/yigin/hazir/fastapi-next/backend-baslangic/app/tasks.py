"""Celery görevleri (queue eki)."""

from app.worker import celery_app


@celery_app.task
def ping(mesaj: str = "pong") -> str:
    """Kuyruğun çalıştığını gösteren örnek görev."""
    return mesaj
