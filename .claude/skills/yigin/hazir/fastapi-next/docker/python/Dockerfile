# FastAPI, Celery ve Alembic için Python imajı. Build bağlamı proje köküdür.
# dev: kod ./backend klasöründen bağlanır, uvicorn --reload. prod: kod imaja kopyalanır.
# Bağımlılıklar backend/requirements.txt içindedir; dosya değişince imaj yeniden build edilir.

FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
# app kullanıcısı bilgisayardaki kullanıcıyla aynı kimliği alır; ./backend altında root sahibi dosya oluşmaz.
ARG UID=1000
ARG GID=1000
RUN groupadd -g "$GID" app && useradd -m -u "$UID" -g "$GID" app
WORKDIR /app
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

FROM base AS dev
# Test araçları (pytest, httpx) yalnızca geliştirme imajına kurulur.
COPY backend/requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install -r /tmp/requirements-dev.txt
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod
COPY --chown=app:app backend/ /app/
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*"]
