import json
import pika
import config

def publish_job(job_id: str):
    """Đẩy message job vào queue."""
    conn = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
    try:
        ch = conn.channel()
        # durable=True: queue sống sót khi RabbitMQ restart.
        ch.queue_declare(queue=config.QUEUE_NAME, durable=True)
        ch.basic_publish(
            exchange="",
            routing_key=config.QUEUE_NAME,
            body=json.dumps({"job_id": job_id}),
            # delivery_mode=2: message được ghi xuống đĩa (persistent) -> không mất khi restart.
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        conn.close()