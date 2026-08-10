import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

import storage
import broker
from models import init_db, SessionLocal, Job

# whitelist định dạng + giới hạn dung lượng (NFR bảo mật)
ALLOWED = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
MAX_BYTES = 10 * 1024 * 1024  # 10 MB

# quy ước tên biến thể — worker sẽ tạo đúng các key này
VARIANTS = {"thumbnail": "thumbnail.jpg", "medium": "medium.jpg", "webp": "image.webp"}


@asynccontextmanager
async def lifespan(app):
    init_db()               # tạo bảng nếu chưa có
    storage.ensure_bucket() # tự tạo bucket — bootstrap không cần tay
    yield


app = FastAPI(title="PixelPipe API", version="0.1.0", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)   # /metrics cho Prometheus


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/images")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"unsupported type: {file.content_type}")
    data = file.file.read()          # đọc SYNC (bỏ 'await file.read()')
    if not data:
        raise HTTPException(status_code=400, detail="empty file")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="file too large")

    job_id = str(uuid.uuid4())
    ext = ALLOWED[file.content_type]
    original_key = f"{job_id}/original.{ext}"

    # ---- THỨ TỰ a -> b -> c (xem docs/decisions/m1-upload-flow.md) ----
    storage.upload_bytes(original_key, data, file.content_type)              # (a) lưu file gốc
    with SessionLocal() as db:                                               # (b) tạo job record
        db.add(Job(id=job_id, status="queued", original_key=original_key))
        db.commit()
    broker.publish_job(job_id)                                              # (c) enqueue CUỐI cùng

    return {"job_id": job_id, "status": "queued"}


@app.get("/images/{job_id}")
def get_image(job_id: str):
    with SessionLocal() as db:
        job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")

    resp = {"job_id": job.id, "status": job.status}
    if job.status == "failed":
        resp["error"] = job.error
    if job.status == "done":
        # chỉ trả URL biến thể khi đã xử lý xong
        resp["variants"] = {
            name: storage.presigned_url(f"{job_id}/{key}")
            for name, key in VARIANTS.items()
        }
    return resp