"""API kökü: bütün uç noktalar /api altında, sürüm önekiyle durur.

Sürümleme kuralı:
- Her sürüm kendi paketindedir: app/api/v1/, app/api/v2/ ...
- Yeni bir sürüm eski sürümü kaldırmaz; ikisi birlikte yayında kalır.
- Geriye uyumsuz bir değişiklik yeni sürüme yazılır; uyumlu ekleme mevcut sürüme yapılabilir.
- Yeni sürüm açıldığında aşağıya bir include_router satırı eklenir.
"""

from fastapi import APIRouter

from app.api.v1 import router as v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)
