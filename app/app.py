from __future__ import annotations

import os
from flask import Flask
from flask_cors import CORS

from app.utils.config import settings
from app.utils.db import init_db
from app.api import api_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # Basic configuration
    app.config["JSON_SORT_KEYS"] = False

    # Enable CORS for all routes (adjust in production)
    CORS(app)

    # Initialize DB tables
    init_db()

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix="/api")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=settings.host, port=settings.port, debug=settings.debug)