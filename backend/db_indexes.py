"""Indices requeridos por los patrones de consulta de la API."""


def ensure_indexes(database):
    """Crea el indice usado para buscar usuarios durante el login."""
    database.usuarios.create_index(
        "email",
        unique=True,
        name="uq_usuarios_email",
    )
