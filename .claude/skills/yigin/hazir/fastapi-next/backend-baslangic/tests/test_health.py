from sqlalchemy import text

from app.db import SessionLocal


async def test_saglik_kontrolu(istemci):
    yanit = await istemci.get("/api/v1/health")
    assert yanit.status_code == 200
    assert yanit.json() == {"status": "ok", "version": "v1", "db": "ok", "redis": "ok"}


async def test_olmayan_surum_404(istemci):
    assert (await istemci.get("/api/v2/health")).status_code == 404


async def test_testler_testing_veritabaninda_calisir():
    async with SessionLocal() as oturum:
        assert (await oturum.execute(text("SELECT current_database()"))).scalar() == "testing"
