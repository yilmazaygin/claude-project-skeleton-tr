"""FastAPI uygulaması.

Uç noktalar /api/v1/... altındadır (app/api/). Belgeler de /api altında durur:
/api/docs ve /api/openapi.json. Böylece Next.js proxy'si üzerinden de açılırlar.
"""

from fastapi import FastAPI

from app.api import router as api_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)
app.include_router(api_router)
