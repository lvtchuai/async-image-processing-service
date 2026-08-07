import io
import json
import pika
from PIL import Image

import config
import storage
from models import SessionLocal, Job


def process_image(data: bytes) -> dict:
    """Tạo các biến thể. Trả {suffix: (bytes, content_type)}."""
    def to_bytes(img, fmt):
        buf = io.BytesIO(); img.save(buf, format=fmt); return buf.getvalue()

    src = Image.open(io.BytesIO(data)).convert("RGB")
    variants = {}

    thumb = src.copy(); thumb.thumbnail((150, 150))
    variants["thumbnail.jpg"] = (to_bytes(thumb, "JPEG"), "image/jpeg")

    medium = src.copy(); medium.thumbnail((800, 800))
    variants["medium.jpg"] = (to_bytes(medium, "JPEG"), "image/jpeg")
    variants["image.webp"] = (to_bytes(medium, "WEBP"), "image/webp")
    return variants


def handle_job(job_id: str):
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if job is None:
            print(f"[warn] job {job_id} không có trong DB, bỏ qua"); return
        job.status = "processing"; db.commit()
        original_key = job.original_key

    try:
        data = storage.download_bytes(original_key)
        for suffix, (blob, ctype) in process_image(data).items():
            # key theo job_id -> xử lý lại chỉ GHI ĐÈ -> IDEMPOTENT
            storage.upload_bytes(f"{job_id}/{suffix}", blob, ctype)
        with SessionLocal() as db:
            db.get(Job, job_id).status = "done"; db.commit()
        print(f"[ok] {job_id} done")
    except Exception as err:
        with SessionLocal() as db:
            j = db.get(Job, job_id); j.status = "failed"; j.error = str(err)[:500]; db.commit()
        print(f"[fail] {job_id}: {err}")


def on_message(ch, method, properties, body):
    job_id = json.loads(body)["job_id"]
    print(f"[recv] {job_id}")
    handle_job(job_id)
    ch.basic_ack(delivery_tag=method.delivery_tag)   # ack SAU khi xử lý xong


def main():
    conn = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
    ch = conn.channel()
    ch.queue_declare(queue=config.QUEUE_NAME, durable=True)
    ch.basic_qos(prefetch_count=1)   # mỗi worker ôm 1 job/lúc -> chia đều, hợp với autoscale
    ch.basic_consume(queue=config.QUEUE_NAME, on_message_callback=on_message)
    print("worker waiting for jobs...")
    ch.start_consuming()


if __name__ == "__main__":
    main()
