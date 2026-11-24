"""Celery uygulaması (queue eki).

Kuyruklar: high, default, low (kısa işler, "worker" servisi) ve long (uzun işler, "worker-long").
Görev göndermek: ping.delay()  ·  uzun iş: uzun_gorev.apply_async(queue="long")
Görevler app/tasks.py içindedir; yeni görev modülleri include listesine eklenir.

Not: Redis aracısında Celery kuyrukları katı öncelikle değil, sırayla okur.
high kuyruğunun her zaman önce işlenmesi gerekiyorsa ona ayrı bir worker açılır.
"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "app",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_default_queue="default",
    timezone="UTC",
    broker_connection_retry_on_startup=True,
    # Zamanlanmış görevler (scheduler eki, celery beat). Örnek:
    # beat_schedule={"her-dakika-ping": {"task": "app.tasks.ping", "schedule": 60.0}},
    beat_schedule={},
)
