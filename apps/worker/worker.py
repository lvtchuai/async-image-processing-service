import io
import json
import pika
from PIL import Image

import config
import storage
from models import SessionLocal, Job
from PIL import Image, UnidentifiedImageError

# Lỗi "độc" (deterministic): retry vô ích -> thẳng DLQ
POISON_ERRORS = (UnidentifiedImageError,)

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


def _fail(job_id: str, msg: str):
    with SessionLocal() as db:
        j = db.get(Job, job_id)
        if j:
            j.status = "failed"; j.error = msg[:500]; db.commit()


def handle_job(job_id: str) -> str:
    """Trả về quyết định: 'ack' | 'retry' | 'dlq'."""
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if job is None:
            print(f"[warn] {job_id} không có trong DB"); return "ack"
        job.attempts += 1              # đếm số lần thử
        job.status = "processing"
        attempts = job.attempts
        original_key = job.original_key
        db.commit()

    try:
        data = storage.download_bytes(original_key)
        for suffix, (blob, ctype) in process_image(data).items():
            storage.upload_bytes(f"{job_id}/{suffix}", blob, ctype)   # key theo job_id -> idempotent
        with SessionLocal() as db:
            db.get(Job, job_id).status = "done"; db.commit()
        print(f"[ok] {job_id} done"); return "ack"

    except POISON_ERRORS as err:       # lỗi độc -> DLQ ngay, không
        _fail(job_id, f"poison: {err}")
        print(f"[poison->dlq] {job_id}: {err}"); return "dlq"

    except Exception as err:           # lỗi tạm -> retry có giới h
        if attempts < config.MAX_ATTEMPTS:
            print(f"[retry {attempts}/{config.MAX_ATTEMPTS}] {job_id}")
        _fail(job_id, f"exhausted after {attempts}: {err}")
        print(f"[exhausted->dlq] {job_id}: {err}"); return "dlq"


def on_message(ch, method, properties, body):
    job_id = json.loads(body)["job_id"]
    print(f"[recv] {job_id}")
    decision = handle_job(job_id)
    if decision == "ack":
        ch.basic_ack(delivery_tag=method.delivery_tag)
    elif decision == "retry":
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)   # trả lại queue -> thử lại
    else:  # dlq
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # requeue=False -> dead-letter sang DLQ


def main():
    conn = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
    ch = conn.channel()
    ch.queue_declare(queue=config.DLQ_NAME, durable=True)
    ch.queue_declare(queue=config.QUEUE_NAME, durable=True, arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": config.DLQ_NAME,
    })
    ch.basic_qos(prefetch_count=1)   # mỗi worker ôm 1 job/lúc -> chia đều, hợp với autoscale
    ch.basic_consume(queue=config.QUEUE_NAME, on_message_callback=on_message)
    print("worker waiting for jobs...")
    ch.start_consuming()


if __name__ == "__main__":
    main()
