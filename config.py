from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "3306"))
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")
    staging_db: str = os.getenv("STAGING_DB", "employee_staging")
    oltp_db: str = os.getenv("OLTP_DB", "employee_oltp")
    olap_db: str = os.getenv("OLAP_DB", "employee_dw")


settings = Settings()
