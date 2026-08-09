import json
import pika
import config

def _declare(ch):
    # DLQ trước
    ch.queue_declare(queue=config.DLQ_NAME, durable=True)
    # queue chính trỏ dead-letter về DLQ (dùng default exchange "" + routing key = tên DLQ)
    ch.queue_declare(queue=config.QUEUE_NAME, durable=True, arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": config.DLQ_NAME,
    })

def publish_job(job_id: str):
    conn = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
    try:
        ch = conn.channel()
        _declare(ch)
        ch.basic_publish(
            exchange="", routing_key=config.QUEUE_NAME,
            body=json.dumps({"job_id": job_id}),
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        conn.close()