"""Casos del SQAP que no tenian una prueba automatizada 1:1.

Cada test de este modulo implementa un caso de prueba concreto de la matriz de
trazabilidad del SQAP (seccion 8) y esta referenciado desde
``metricas/trazabilidad.json``. El calculador de metricas
(``metricas/calcular_metricas.py``) falla si alguno de estos nodeids desaparece,
de modo que la matriz del documento no puede quedar desactualizada en silencio.
"""


def test_cp06_login_admin_redirige_al_panel(client, usuario_admin):
    """CP-06 --- Login de administrador va al panel (RF-02)."""
    r = client.post("/api/login", json={
        "email": usuario_admin["email"], "password": usuario_admin["password"],
    })
    assert r.status_code == 200
    assert r.get_json()["redirect"] == "/admin/home"

    r_user = client.get("/api/user")
    assert r_user.status_code == 200
    assert r_user.get_json()["rol"] == "administrador"


def test_cp13_carrito_rechaza_cantidad_negativa(client, usuario_cliente, db):
    """CP-13 --- El carrito rechaza cantidades negativas (RF-04, valores limite)."""
    prod_id = db.productos.insert_one({"nombre": "Ron", "precio": 10}).inserted_id
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]

    r = client.post("/api/cart", json={
        "productos": [{"id": str(prod_id), "cantidad": -1}],
    })

    assert r.status_code == 400
    assert db.carrito.count_documents({}) == 0


def test_cp20_api_user_sin_sesion_401(client):
    """CP-20 --- GET /api/user sin sesion devuelve 401 (RNF-02)."""
    assert client.get("/api/user").status_code == 401
