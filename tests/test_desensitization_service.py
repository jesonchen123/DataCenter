import unittest

from app.services.desensitization_service import desensitize_text


class DesensitizationServiceTest(unittest.TestCase):
    def test_desensitizes_common_sensitive_fields(self):
        text = (
            "张三 手机 13812345678，邮箱 test@example.com，微信 wx_abc123，"
            "QQ 123456789，订单号 ORD20260101001，身份证 110101199001011234。"
        )

        result, changed = desensitize_text(text)

        self.assertTrue(changed)
        self.assertIn("<PHONE>", result)
        self.assertIn("<EMAIL>", result)
        self.assertIn("<WECHAT>", result)
        self.assertIn("<QQ>", result)
        self.assertIn("<ORDER_ID>", result)
        self.assertIn("<ID_CARD>", result)
        self.assertNotIn("13812345678", result)
        self.assertNotIn("test@example.com", result)

    def test_returns_unchanged_flag_for_safe_text(self):
        result, changed = desensitize_text("产品支持企业内部知识库问答。")

        self.assertFalse(changed)
        self.assertEqual(result, "产品支持企业内部知识库问答。")


if __name__ == "__main__":
    unittest.main()
