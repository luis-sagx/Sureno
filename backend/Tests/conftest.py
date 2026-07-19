"""Fixtures compartidas de la suite (TAR-01).

Clave: se parchea config.db con mongomock ANTES de importar app/models, de modo
que ningun test toca Atlas (relacionado con DEF-016). Provee:
  - db              -> base mongomock limpia por test
  - client          -> Flask test client (CSRF desactivado en pruebas)
  - usuario_cliente -> usuario rol cliente ya sembrado
  - usuario_admin   -> usuario rol administrador ya sembrado
"""
import os
import sys
import types

import mongomock
import pytest
import werkzeug

# Compat: algunas builds de werkzeug no exponen __version__ y el test client
# de Flask lo lee al construir el User-Agent.
if not hasattr(werkzeug, "__version__"):
    import importlib.metadata as _md
    werkzeug.__version__ = _md.version("werkzeug")

# --- Parchear config.db ANTES de importar la app (evita conexion a Atlas) ---
_mongo_client = mongomock.MongoClient()
_test_db = _mongo_client["Sureno_test"]
_fake_config = types.ModuleType("config")
_fake_config.db = _test_db
sys.modules["config"] = _fake_config

os.environ.setdefault("SECRET_KEY", "test-secret-key")

import app as app_module  # noqa: E402  (import tardio a proposito)


@pytest.fixture
def db():
    """Base mongomock vaciada al inicio de cada test."""
    for name in _test_db.list_collection_names():
        _test_db.drop_collection(name)
    return _test_db


@pytest.fixture
def client(db):
    """Flask test client con CSRF desactivado para las pruebas."""
    app_module.app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        LOGIN_RATE_LIMIT_IP="60 per minute",
        LOGIN_RATE_LIMIT_IDENTITY="5 per minute",
    )
    app_module.limiter.reset()
    return app_module.app.test_client()


def _seed_usuario(db, *, email, rol, id_rol, password="Password123"):
    import bcrypt
    db.roles.insert_one({"id_rol": id_rol, "rol": rol})
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    inserted = db.usuarios.insert_one({
        "email": email,
        "password": hashed,
        "id_rol": id_rol,
        "nombre": "Ana",
        "apellido": "Prueba",
        "cedula": "0102030405",
    })
    return {"_id": str(inserted.inserted_id), "email": email, "password": password}


@pytest.fixture
def usuario_cliente(db):
    return _seed_usuario(db, email="cliente@test.com", rol="cliente", id_rol=1)


@pytest.fixture
def usuario_admin(db):
    return _seed_usuario(db, email="admin@test.com", rol="administrador", id_rol=2)
