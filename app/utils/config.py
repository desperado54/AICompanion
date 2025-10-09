import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


@dataclass
class Settings:
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "5000"))

    # SQLite database file in project root by default
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///app.db")

    # LLM settings (Ollama)
    # Example model: "llama3.1:8b" or "qwen2.5:7b"
    model_name: str = os.getenv("MODEL_NAME", "llama3.1:8b")
    temperature: float = float(os.getenv("TEMPERATURE", "0.6"))
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


settings = Settings()