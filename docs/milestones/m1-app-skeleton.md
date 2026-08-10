# M1 — App skeleton (chạy local)

## Mục tiêu
Pipeline async chạy được bằng `docker-compose` + Python local: upload ảnh → worker xử lý → done.

## Kiến trúc thêm vào
- **API** (`apps/api`): `POST /images` làm 3 việc **đúng thứ tự a→b→c** (lưu MinIO → tạo job DB →
  enqueue RabbitMQ); `GET /images/{id}` trả status + presigned URL; `/healthz`, `/metrics`.
- **Worker** (`apps/worker`): consume queue → resize bằng Pillow → upload biến thể → cập nhật status.
- **Infra local**: Postgres + RabbitMQ + MinIO qua `docker-compose.yml`.
- Điểm thiết kế: **key biến thể theo `job_id`** → xử lý lại chỉ ghi đè → **idempotent**.

## Lệnh
```bash
# 1. dựng hạ tầng local (3 service nền)
docker compose up -d
#    up = tạo & chạy container; -d = chạy nền (detached)

# 2. môi trường Python cho API
cd apps/api
python3 -m venv .venv          # tạo môi trường ảo (cô lập thư viện)
source .venv/bin/activate      # kích hoạt venv
pip install -r requirements.txt

# 3. tạo bảng jobs trong Postgres
python -c "from models import init_db; init_db()"
#    chạy nhanh 1 lệnh Python -> create_all() tạo bảng

# 4. chạy API (giữ terminal này)
uvicorn main:app --port 8000
#    uvicorn = ASGI server chạy FastAPI; main:app = biến 'app' trong main.py

# 5. chạy worker (terminal khác, venv riêng của apps/worker)
python worker.py

# 6. thử upload + hỏi trạng thái
curl -L -o /tmp/test.jpg https://picsum.photos/800        # tải ảnh mẫu
curl -F "file=@/tmp/test.jpg;type=image/jpeg" http://localhost:8000/images   # -> job_id
curl http://localhost:8000/images/<job_id>               # -> done + URL biến thể

# 7. test (viết ngay từ đầu)
pytest -q
#    chạy unit test: process_image (worker) + validation (api) — không cần infra
```

## Ý nghĩa quan trọng
- **`docker compose up -d`**: một lệnh dựng cả Postgres/RabbitMQ/MinIO — vòng lặp dev nhanh.
- **venv**: mỗi service có thư viện riêng, không lẫn nhau.
- **enqueue cuối cùng (c)**: message chỉ được tạo *sau khi* file + record đã tồn tại → không bao
  giờ có message trỏ tới thứ không tồn tại (xem `decisions/m1-upload-flow.md`).

## Definition of Done
- [ ] Upload → `done`, tải được thumbnail/webp. Test xanh.
