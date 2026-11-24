"""Test ayarları.

Testler yalnızca "testing" veritabanında çalışır (compose.local.yaml içindeki db-test-hazirla açar).
DB_DATABASE, uygulama içe aktarılmadan ÖNCE değiştirilir: ayarlar ve veritabanı bağlantısı
içe aktarma anında kurulur. Ardından bir koruma, bağlantının gerçekten "testing"e gittiğini doğrular.
"""

import os

os.environ["DB_DATABASE"] = "testing"

import subprocess  # noqa: E402

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.config import settings  # noqa: E402

if settings.db_database != "testing":
    raise RuntimeError(f"Testler yalnızca 'testing' veritabanında çalışır; şu an: {settings.db_database}")


@pytest.fixture(scope="session", autouse=True)
def goc_uygula() -> None:
    """Göçleri test veritabanına uygular (geliştirme veritabanına dokunmaz)."""
    subprocess.run(["alembic", "upgrade", "head"], check=True, env={**os.environ, "DB_DATABASE": "testing"})


@pytest.fixture
async def istemci():
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
