from fastapi.testclient import TestClient
from main import app

# KHÔNG dùng `with` -> lifespan (init_db/ensure_bucket) không chạy -> test không cần infra.
client = TestClient(app)


def test_healthz():
    assert client.get("/healthz").status_code == 200


def test_rejects_unsupported_type():
    # từ chối TRƯỚC khi đụng storage/db -> test được mà không cần hạ tầng
    r = client.post("/images", files={"file": ("x.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_rejects_empty_file():
    r = client.post("/images", files={"file": ("x.jpg", b"", "image/jpeg")})
    assert r.status_code == 400
