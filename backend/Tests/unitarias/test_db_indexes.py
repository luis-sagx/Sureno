import pytest
from pymongo.errors import DuplicateKeyError

from db_indexes import ensure_indexes


def test_ensure_indexes_crea_indice_unico_de_email(db):
    ensure_indexes(db)

    usuarios = db.usuarios.index_information()["uq_usuarios_email"]
    assert usuarios["unique"] is True
    assert usuarios["key"] == [("email", 1)]


def test_indice_email_impide_usuarios_duplicados(db):
    ensure_indexes(db)
    db.usuarios.insert_one({"email": "duplicado@test.com"})

    with pytest.raises(DuplicateKeyError):
        db.usuarios.insert_one({"email": "duplicado@test.com"})
