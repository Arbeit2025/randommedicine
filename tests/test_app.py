"""ランダムお薬（randommedicine）のテスト。

外部通信は行わず、内蔵データと Flask テストクライアントで検証する。
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module  # noqa: E402

SAMPLE = {
    "name": "テスト薬",
    "category": "テスト分類",
    "ingredients": "テスト成分A、テスト成分B",
    "effects": "これはテスト用の効果効能です。",
    "points": "テストポイントです。",
    "url": "https://ja.wikipedia.org/wiki/テスト薬",
}


class RandomMedicineTest(unittest.TestCase):
    def setUp(self):
        self.client = app_module.app.test_client()
        self._orig_fetch = app_module.fetch_random_medicine

    def tearDown(self):
        app_module.fetch_random_medicine = self._orig_fetch

    def test_healthz(self):
        res = self.client.get("/healthz")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "ok")

    def test_index_ok(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("ランダムお薬", body)
        self.assertIn("ランダムで薬を表示", body)
        self.assertIn("医療上のアドバイスではなく", body)
        self.assertIn("添付文書", body)

    def test_random_success(self):
        app_module.fetch_random_medicine = lambda: dict(SAMPLE)
        res = self.client.get("/random")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("テスト薬", body)
        self.assertIn("テスト分類", body)
        self.assertIn("テスト成分A", body)
        self.assertIn("これはテスト用の効果効能です。", body)
        self.assertIn("テストポイントです。", body)
        self.assertIn("https://ja.wikipedia.org/wiki/テスト薬", body)
        self.assertIn("Wikipediaで詳しく見る", body)

    def test_random_real_data_has_all_fields(self):
        res = self.client.get("/random")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("主な成分", body)
        self.assertIn("効果・効能", body)
        self.assertIn("一般的なポイント・注意", body)

    def test_dataset_size_and_uniqueness(self):
        medicines = app_module.MEDICINES
        self.assertEqual(len(medicines), 120)
        names = [m["name"] for m in medicines]
        self.assertEqual(len(names), len(set(names)))

    def test_dataset_fields_complete(self):
        for m in app_module.MEDICINES:
            for key in ("name", "category", "ingredients", "effects",
                        "points", "url"):
                self.assertTrue(m[key], (m.get("name"), key))
            self.assertTrue(
                m["url"].startswith("https://ja.wikipedia.org/wiki/"),
                m["name"],
            )

    def test_fetch_returns_copy_from_dataset(self):
        one = app_module.fetch_random_medicine()
        self.assertIn(one["name"], [m["name"] for m in app_module.MEDICINES])
        one["name"] = "書き換え"
        self.assertNotIn(
            "書き換え", [m["name"] for m in app_module.MEDICINES]
        )


if __name__ == "__main__":
    unittest.main()
