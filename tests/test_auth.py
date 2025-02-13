def test_auth_register_and_login(client):
    # Регистрация пользователя при первой аутентификации он будет создан автоматически
    response = client.post("/api/auth", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data

    # Повторный вход с теми же данными должен успешно авторизовать пользователя
    response2 = client.post("/api/auth", json={"username": "testuser", "password": "testpass"})
    assert response2.status_code == 200
    data2 = response2.json()
    assert "token" in data2
