"""Veritabanı modelleri.

Yeni bir model bu pakete ayrı bir dosya olarak eklenir ve aşağıda içe aktarılır.
Alembic (`alembic revision --autogenerate`) modelleri Base.metadata üzerinden görür;
içe aktarılmayan model göç dosyasına girmez.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Örnek: from app.models.user import User  # noqa: E402,F401
