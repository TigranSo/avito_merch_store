def test_transfer_coins(client):
    # Регистрирую двух пользователей sender и recipient
    response_sender = client.post("/api/auth", json={"username": "sender", "password": "pass"})
    token_sender = response_sender.json()["token"]
    headers_sender = {"Authorization": f"Bearer {token_sender}"}
    
    response_recipient = client.post("/api/auth", json={"username": "recipient", "password": "pass"})
    token_recipient = response_recipient.json()["token"]
    headers_recipient = {"Authorization": f"Bearer {token_recipient}"}
    
    # Получаю баланс отправителя до перевода
    response_info_sender_before = client.get("/api/info", headers=headers_sender)
    coins_sender_before = response_info_sender_before.json()["coins"]
    
    # Передаю 100 монет от sender к recipient
    transfer_amount = 100
    response_transfer = client.post("/api/sendCoin", json={"toUser": "recipient", "amount": transfer_amount}, headers=headers_sender)
    assert response_transfer.status_code == 200
    
    # Проверяю баланс отправителя после перевода
    response_info_sender_after = client.get("/api/info", headers=headers_sender)
    coins_sender_after = response_info_sender_after.json()["coins"]
    assert coins_sender_after == coins_sender_before - transfer_amount
    
    # Проверка что recipient получил монеты
    response_info_recipient = client.get("/api/info", headers=headers_recipient)
    coin_history = response_info_recipient.json()["coinHistory"]
    received = coin_history.get("received", [])
    # Ищу запись sender является отправителем
    assert any(tx["fromUser"] == "sender" and tx["amount"] == transfer_amount for tx in received)
