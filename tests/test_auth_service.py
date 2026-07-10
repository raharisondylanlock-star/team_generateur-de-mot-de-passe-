import os
import tempfile
import unittest

from security.auth_service import AuthService


class AuthServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = os.path.join(self.temp_dir.name, "users.json")
        self.auth = AuthService(storage_path=self.storage_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register_and_authenticate(self):
        self.assertTrue(self.auth.register_user("alice", "secret123"))
        self.assertTrue(self.auth.authenticate("alice", "secret123"))
        self.assertFalse(self.auth.authenticate("alice", "wrongpass"))
        self.assertFalse(self.auth.authenticate("bob", "secret123"))

    def test_register_without_password_generates_a_random_one(self):
        self.assertTrue(self.auth.register_user("alice"))
        self.assertTrue(self.auth.last_generated_password)
        self.assertTrue(self.auth.authenticate("alice", self.auth.last_generated_password))

    def test_change_password_after_login(self):
        self.assertTrue(self.auth.register_user("alice"))
        generated_password = self.auth.last_generated_password

        self.assertTrue(self.auth.change_password("alice", generated_password, "newSecret123"))
        self.assertTrue(self.auth.authenticate("alice", "newSecret123"))
        self.assertFalse(self.auth.authenticate("alice", generated_password))


if __name__ == "__main__":
    unittest.main()
