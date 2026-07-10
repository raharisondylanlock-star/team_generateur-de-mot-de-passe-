import os
import tempfile
import unittest

from security.password_service import PasswordService


class PasswordServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = os.path.join(self.temp_dir.name, "passwords.json")
        self.service = PasswordService(storage_path=self.storage_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_list_passwords_separated_by_user(self):
        self.service.add_password("alice", "GitHub", "alice@example.com", "secret123")
        self.service.add_password("alice", "Gmail", "alice@example.com", "abc123")
        self.service.add_password("bob", "GitHub", "bob@example.com", "xyz789")

        alice_entries = self.service.list_passwords("alice")
        bob_entries = self.service.list_passwords("bob")

        self.assertEqual(len(alice_entries), 2)
        self.assertEqual(len(bob_entries), 1)
        self.assertEqual(alice_entries[0]["site"], "GitHub")
        self.assertEqual(alice_entries[1]["site"], "Gmail")
        self.assertEqual(bob_entries[0]["password"], "xyz789")

    def test_delete_password(self):
        entry_id = self.service.add_password("alice", "GitHub", "alice@example.com", "secret123")
        self.assertTrue(self.service.delete_password("alice", entry_id))
        self.assertEqual(self.service.list_passwords("alice"), [])
        self.assertFalse(self.service.delete_password("alice", entry_id))


if __name__ == "__main__":
    unittest.main()
