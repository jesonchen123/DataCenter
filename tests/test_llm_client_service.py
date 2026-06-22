import unittest

from app.core.config import Settings
from app.services.llm_client_service import OpenAICompatibleLLMClient, is_llm_configured


class LLMClientServiceTest(unittest.TestCase):
    def test_is_llm_configured_rejects_placeholder_keys(self):
        settings = Settings(llm_api_key="your_api_key")

        self.assertFalse(is_llm_configured(settings))

    def test_chat_sends_openai_compatible_request_and_parses_content(self):
        calls = []

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "id": "chatcmpl_test",
                    "choices": [
                        {
                            "message": {
                                "content": "{\"title\":\"知识片段\"}",
                            }
                        }
                    ],
                    "usage": {"total_tokens": 12},
                }

        def fake_post(url, headers, json, timeout):
            calls.append(
                {
                    "url": url,
                    "headers": headers,
                    "json": json,
                    "timeout": timeout,
                }
            )
            return FakeResponse()

        settings = Settings(
            llm_api_base_url="https://llm.example.com/api/v3",
            llm_api_key="secret_key",
            llm_model_name="model_001",
            llm_temperature=0.1,
            llm_max_tokens=512,
            llm_timeout=30,
        )
        client = OpenAICompatibleLLMClient(settings=settings, post=fake_post)

        result = client.chat(
            messages=[{"role": "user", "content": "生成知识片段"}],
            response_format={"type": "json_object"},
        )

        self.assertEqual(result.content, "{\"title\":\"知识片段\"}")
        self.assertEqual(result.response_payload["id"], "chatcmpl_test")
        self.assertEqual(result.request_payload["model"], "model_001")
        self.assertEqual(calls[0]["url"], "https://llm.example.com/api/v3/chat/completions")
        self.assertEqual(calls[0]["headers"]["Authorization"], "Bearer secret_key")
        self.assertEqual(calls[0]["json"]["response_format"], {"type": "json_object"})
        self.assertEqual(calls[0]["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
