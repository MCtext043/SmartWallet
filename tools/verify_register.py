import os
import asyncio
import uuid
import sys
from pathlib import Path

import httpx

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


async def main():
    # Важно: задаём DATABASE_URL ДО импорта main.py,
    # т.к. при импорте создаются таблицы.
    os.environ["DATABASE_URL"] = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/smartwallet",
    )

    import main as app_main

    transport = httpx.ASGITransport(app=app_main.app, raise_app_exceptions=True)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        phone = "+7999" + str(uuid.uuid4().int)[:8]
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        payload = {"phone": phone, "email": email, "name": "Verify", "password": "123456"}

        r = await client.post("/auth/register", json=payload)
        print("status_code:", r.status_code)
        print("response_json:", r.json())


if __name__ == "__main__":
    asyncio.run(main())

