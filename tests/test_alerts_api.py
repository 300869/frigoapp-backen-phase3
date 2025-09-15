import pytest
from fastapi.testclient import TestClient

from freshkeeper.main import freshkeeper

client = TestClient(app)




def test_create_and_ack_alert(db_session):
# create
payload = {
"product_id": 1,
"kind": "SOON",
"message": "Bientôt périmé",
"due_date": "2025-09-06",
}
r = client.post("/alerts/", json=payload)
assert r.status_code == 201
alert = r.json()
assert alert["is_ack"] is False


# ack
r2 = client.post(f"/alerts/{alert['id']}/ack")
assert r2.status_code == 200
assert r2.json()["is_ack"] is True
