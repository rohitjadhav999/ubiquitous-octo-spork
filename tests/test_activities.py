from fastapi.testclient import TestClient
from src import app as application
from urllib.parse import quote

client = TestClient(application.app)


def unique_email(base="tester@mergington.edu"):
    # generate a random-ish email using id() to avoid collisions across runs
    return base.replace("@", f"+{abs(id(base)) % 10000}@")


def test_signup_and_get_immediate():
    activity = "Programming Class"
    email = "tester_immediate@mergington.edu"

    # ensure not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # sign up
    post = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert post.status_code == 200
    assert "Signed up" in post.json()["message"]

    # fetch activities immediately and verify participant is present
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    assert email in resp2.json()[activity]["participants"]

    # cleanup
    del_resp = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")
    assert del_resp.status_code == 200
    after = client.get("/activities").json()[activity]["participants"]
    assert email not in after


def test_delete_nonexistent_participant_returns_404():
    activity = "Chess Club"
    email = "doesnotexist@mergington.edu"

    del_resp = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")
    assert del_resp.status_code == 404


def test_signup_then_delete_participant():
    activity = "Tennis Club"
    email = "tempdelete@mergington.edu"

    # sign up
    post = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert post.status_code == 200

    # delete
    del_resp = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")
    assert del_resp.status_code == 200

    # verify gone
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
