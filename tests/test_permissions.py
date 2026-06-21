import unittest

from app.core.permissions import can_approve, can_export, can_view_audit_logs
from app.domain.enums import Role


class PermissionRulesTest(unittest.TestCase):
    def test_manager_can_approve_export_and_view_audit_logs(self):
        self.assertTrue(can_approve(Role.MANAGER.value))
        self.assertTrue(can_export(Role.MANAGER.value))
        self.assertTrue(can_view_audit_logs(Role.MANAGER.value))

    def test_normal_user_cannot_approve_export_or_view_audit_logs(self):
        self.assertFalse(can_approve(Role.NORMAL_USER.value))
        self.assertFalse(can_export(Role.NORMAL_USER.value))
        self.assertFalse(can_view_audit_logs(Role.NORMAL_USER.value))

    def test_unknown_role_has_no_privileged_permissions(self):
        self.assertFalse(can_approve("sales"))
        self.assertFalse(can_export("sales"))
        self.assertFalse(can_view_audit_logs("sales"))


if __name__ == "__main__":
    unittest.main()
