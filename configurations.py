import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
MODEL = "gpt-oss:20b"