import os

# Có default để chạy local; production override bằng biến môi trường.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://pixel:pixel@localhost:5432/pixelpipe")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME   = os.getenv("QUEUE_NAME", "image_jobs")

S3_ENDPOINT   = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET     = os.getenv("S3_BUCKET", "pixelpipe")
S3_REGION     = os.getenv("S3_REGION", "us-east-1")