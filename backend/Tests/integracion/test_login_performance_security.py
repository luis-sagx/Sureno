import app as app_module


def test_login_rol_conocido_no_consulta_coleccion_roles(
    client, db, usuario_cliente, monkeypatch
):
    def unexpected_query(*_args, **_kwargs):
        raise AssertionError("el login normal no debe consultar roles")

    monkeypatch.setattr(db.roles, "find_one", unexpected_query)
    response = client.post("/api/login", json={
        "email": usuario_cliente["email"],
        "password": usuario_cliente["password"],
    })

    assert response.status_code == 200
    assert response.get_json()["redirect"] == "/"


def test_rate_limit_bloquea_intentos_repetidos_por_identidad(client):
    app_module.app.config.update(
        LOGIN_RATE_LIMIT_IP="100 per minute",
        LOGIN_RATE_LIMIT_IDENTITY="3 per minute",
    )
    app_module.limiter.reset()
    payload = {"email": "objetivo@test.com", "password": "incorrecta"}

    for _ in range(3):
        assert client.post("/api/login", json=payload).status_code == 404

    blocked = client.post("/api/login", json=payload)
    assert blocked.status_code == 429
    assert "Demasiados intentos" in blocked.get_json()["error"]
    assert blocked.headers["X-RateLimit-Remaining"] == "0"
    assert "Retry-After" in blocked.headers


def test_rate_limit_bloquea_multiples_identidades_desde_una_ip(client):
    app_module.app.config.update(
        LOGIN_RATE_LIMIT_IP="3 per minute",
        LOGIN_RATE_LIMIT_IDENTITY="100 per minute",
    )
    app_module.limiter.reset()

    for index in range(3):
        response = client.post("/api/login", json={
            "email": f"objetivo-{index}@test.com",
            "password": "incorrecta",
        })
        assert response.status_code == 404

    blocked = client.post("/api/login", json={
        "email": "otra-identidad@test.com",
        "password": "incorrecta",
    })
    assert blocked.status_code == 429
