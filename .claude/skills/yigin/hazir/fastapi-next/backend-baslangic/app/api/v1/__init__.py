"""API sürüm 1: /api/v1/...

Bu sürümün her uç nokta grubu ayrı bir modüldür ve burada bağlanır.
"""

from fastapi import APIRouter

from app.api.v1 import health

router = APIRouter(prefix="/v1")
router.include_router(health.router)
