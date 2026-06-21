import unittest

from app.core.config import Settings


class SettingsTest(unittest.TestCase):
    def test_default_settings_match_backend_mvp_contract(self):
        settings = Settings()

        self.assertEqual(settings.app_name, "chat-data-platform")
        self.assertIn("postgresql+psycopg2://", settings.database_url)
        self.assertEqual(settings.redis_url, "redis://localhost:6379/0")


if __name__ == "__main__":
    unittest.main()
