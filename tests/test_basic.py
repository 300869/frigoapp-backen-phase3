def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_products_list(client):
    r = client.get("/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_products_crud_and_alerts(client, category_id):
    payload = {
        "name": "TEST_PY",
        "category_id": category_id,
        "quantity": 0,
        "location": "PyBin",
        "expiry_date": "2025-12-31",
    }
    r = client.post("/products", json=payload)
    assert r.status_code in (200, 201)
    prod = r.json()
    pid = prod["id"]

    # L'endpoint alerts ne doit pas planter
    r = client.get("/alerts", params={"status": "OPEN"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # Monte la quantité => ferme l'alerte STOCK_BAS
    r = client.put(f"/products/{pid}", json={"quantity": 5})
    assert r.status_code == 200
    assert r.json()["quantity"] == 5
