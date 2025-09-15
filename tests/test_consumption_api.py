from fastapi.testclient import TestClient

from freshkeeper.main import freshkeeper

client = TestClient(app)




def test_post_consumption(db_session):
payload = {
"product_id": 1,
"quantity": 0.5,
"unit": "kg",
"consumed_at": "2025-09-05T12:00:00",
}
r = client.post("/consumption/", json=payload)
assert r.status_code == 201
body = r.json()
assert body["product_id"] == 1
assert body["quantity"] == 0.5
