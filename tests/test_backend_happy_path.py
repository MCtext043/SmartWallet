import os
import uuid
import asyncio
import unittest
from unittest.mock import patch

import httpx


class DummyResponse:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text


class TestBackendHappyPath(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Важно: задаём DATABASE_URL ДО импорта main.py, т.к. таблицы создаются при import.
        os.environ["DATABASE_URL"] = os.getenv(
            "TEST_DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/smartwallet",
        )

        # Импортируем app только после настройки переменной окружения.
        import main

        self.app = main.app

    async def test_full_happy_path(self):
        import main  # для ссылок на роутеры/джойна

        async def asgi_client():
            transport = httpx.ASGITransport(app=self.app, raise_app_exceptions=True)
            return httpx.AsyncClient(transport=transport, base_url="http://test")

        phone = "+7" + str(uuid.uuid4().int)[:10]
        email = f"{uuid.uuid4().hex[:10]}@example.com"
        password = "123456"
        name = "HappyPath User"

        async with await asgi_client() as client:
            # 1) Register
            r = await client.post(
                "/auth/register",
                json={"phone": phone, "email": email, "name": name, "password": password},
            )
            self.assertEqual(r.status_code, 200, r.text)
            reg = r.json()
            self.assertIn("id", reg)

            # 2) Login
            r = await client.post(
                "/auth/login",
                json={"phone": phone, "password": password},
            )
            self.assertEqual(r.status_code, 200, r.text)
            token = r.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # 3) Profile
            r = await client.get("/auth/profile", headers=headers)
            self.assertEqual(r.status_code, 200, r.text)
            profile = r.json()
            self.assertEqual(profile["phone"], phone)

            # 4) Create card
            cashback_rules = {"еда": 5, "транспорт": 3, "прочее": 1}
            r = await client.post(
                "/cards/",
                headers=headers,
                json={
                    "bank_name": "Test Bank",
                    "card_name": "Test Card",
                    "last4": "1234",
                    "cashback_rules": cashback_rules,
                    "limit_monthly": 10000.0,
                },
            )
            self.assertEqual(r.status_code, 200, r.text)
            card = r.json()
            card_id = card["id"]

            # 5) Get cards list + card by id
            r = await client.get("/cards/", headers=headers)
            self.assertEqual(r.status_code, 200, r.text)
            cards = r.json()
            self.assertTrue(any(c["id"] == card_id for c in cards))

            r = await client.get(f"/cards/{card_id}", headers=headers)
            self.assertEqual(r.status_code, 200, r.text)

            # 6) Create transaction
            r = await client.post(
                "/transactions/",
                headers=headers,
                json={"card_id": card_id, "amount": 2000.0, "category": "еда"},
            )
            self.assertEqual(r.status_code, 200, r.text)
            tx = r.json()
            self.assertGreaterEqual(tx["cashback_earned"], 0)

            # 7) Transactions list
            r = await client.get("/transactions/", headers=headers)
            self.assertEqual(r.status_code, 200, r.text)
            txs = r.json()
            self.assertTrue(any(t["id"] == tx["id"] for t in txs))

            # 8) Recommendations
            r = await client.get("/assistant/recommendations", headers=headers)
            self.assertEqual(r.status_code, 200, r.text)
            recs = r.json()
            self.assertIsInstance(recs, list)

            # 9) Cashback best-card
            r = await client.get("/cashback/best-card", headers=headers, params={"category": "еда"})
            self.assertEqual(r.status_code, 200, r.text)
            best = r.json()
            self.assertEqual(best["card_id"], card_id)
            self.assertEqual(best["category"], "еда")

            # 10) Assistant chat (mock external request)
            giga_text = '{"content":"Ответ ассистента: тест\\nГотово"}'

            def fake_requests_post(*args, **kwargs):
                return DummyResponse(200, giga_text)

            with patch.object(main.assistant.requests, "post", side_effect=fake_requests_post):
                # Важно: асинхронный клиент вызывает endpoint в threadpool,
                # поэтому подмена должна быть активна во время запроса.
                r = await client.post(
                    "/assistant/chat",
                    headers=headers,
                    json={"message": "Привет, тест!"}
                )
                self.assertEqual(r.status_code, 200, r.text)
                chat = r.json()
                self.assertIn("Ответ ассистента", chat["reply"])
                self.assertIn("\n", chat["reply"])


if __name__ == "__main__":
    unittest.main()

