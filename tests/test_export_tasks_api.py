import unittest
from types import SimpleNamespace

from app.domain.enums import Role

try:
    from app.api.v1 import export_tasks
except ModuleNotFoundError:  # pragma: no cover
    export_tasks = None


class _Query:
    def __init__(self, result):
        self.result = result

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.result


class _DB:
    def __init__(self, result):
        self.result = result

    def query(self, *_args, **_kwargs):
        return _Query(self.result)


@unittest.skipIf(export_tasks is None or export_tasks.router is None, "fastapi is not installed")
class ExportTasksApiTest(unittest.TestCase):
    def test_get_export_content_returns_only_qa_documents(self):
        task = SimpleNamespace(
            export_content={
                "export_id": "export_001",
                "documents": [
                    {
                        "doc_id": "kb_001",
                        "title": "产品使用流程",
                        "content": "客户问：产品怎么使用？\n销售答：先登录后台再创建知识库。",
                        "metadata": {"risk_level": "low"},
                        "security": {"price_filtered": True},
                    }
                ],
            }
        )

        result = export_tasks.get_export_content(
            "00000000-0000-0000-0000-000000000001",
            current_user=SimpleNamespace(role=Role.MANAGER.value),
            db=_DB(task),
        )

        self.assertEqual(
            result,
            {
                "documents": [
                    {
                        "content": "客户问：产品怎么使用？\n销售答：先登录后台再创建知识库。",
                    }
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
