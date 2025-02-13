import pytest

def test_purchase_merch(client):
    # Создаю пользователя
    response = client.post("/api/auth", json={"username": "buyer", "password": "pass"})
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Проверка что список мерча не пуст
    response_merch = client.get("/api/merch", headers=headers)
    assert response_merch.status_code == 200
    merch_list = response_merch.json()
    if not merch_list:
        pytest.skip("No merch items available")
    merch_item = merch_list[0]
    
    # Получаю баланс до покупки
    response_info_before = client.get("/api/info", headers=headers)
    coins_before = response_info_before.json()["coins"]
    price = merch_item["price"]
    
    # Выполняю покупку
    response_buy = client.get(f"/api/buy/{merch_item['name']}", headers=headers)
    assert response_buy.status_code == 200
    assert f"Purchased {merch_item['name']} successfully" in response_buy.json().get("message", "")
    
    # Проверяю баланс после покупки
    response_info_after = client.get("/api/info", headers=headers)
    coins_after = response_info_after.json()["coins"]
    assert coins_after == coins_before - price
