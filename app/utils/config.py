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

    # LLM settings
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    temperature: float = float(os.getenv("TEMPERATURE", "0.6"))


settings = Settings()