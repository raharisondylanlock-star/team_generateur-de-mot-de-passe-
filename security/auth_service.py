import hashlib
import json
import os
import secrets
import string
from pathlib import Path
from typing import Dict, Set


# MySQL is optional at runtime.
# Import it lazily only when we actually use MySQL.

try:
    from mysql_client import ensure_schema, get_mysql_connection
except Exception:  # MySQL not installed / not configured
    ensure_schema = None
    get_mysql_connection = None




# NOTE: this project has a top-level file named `database.py`.
# Avoid importing it from here.



class AuthService:
    def __init__(
        self,
        storage_path: str | None = None,
        admins_path: str | None = None,
        use_mysql: bool | None = None,
    ):
        """AuthService.

        - By default, it uses MySQL if MYSQL_DATABASE is reachable.
        - Otherwise it falls back to JSON (backward compatible).

        The public API stays identical:
          register_user, authenticate, change_password, is_admin, generate_password
        """

        # Legacy fallback paths
        if storage_path is None:
            storage_path = Path(__file__).resolve().parents[1] / "database" / "users.json"
        if admins_path is None:
            admins_path = Path(__file__).resolve().parents[1] / "database" / "admins.json"

        self.storage_path = Path(storage_path)
        self.admins_path = Path(admins_path)

        # Decide mode
        if use_mysql is None:
            # If env is set (or any mysql config exists), try mysql.
            use_mysql = bool(os.getenv("MYSQL_HOST") or os.getenv("MYSQL_DATABASE") or os.getenv("MYSQL_USER"))

        self.use_mysql = bool(use_mysql)

        # Hashing state
        self.last_generated_password: str | None = None

        # Initialize JSON fallback storage
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.admins_path.parent.mkdir(parents=True, exist_ok=True)

        self._users: Dict[str, str] = {}
        if not self.use_mysql:
            self._users = self._load()

        # Ensure schema in mysql if enabled
        if self.use_mysql:
            try:
                ensure_schema()
            except Exception:
                # If mysql is not available, fallback
                self.use_mysql = False
                self._users = self._load()

    # ------------------------ Legacy JSON helpers ------------------------
    def _load_admins(self) -> Set[str]:
        if not self.admins_path.exists():
            self.admins_path.write_text("[]", encoding="utf-8")
            return set()

        try:
            data = json.loads(self.admins_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return set()

        if not isinstance(data, list):
            return set()
        return {str(x) for x in data}

    def _load(self) -> Dict[str, str]:
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")
            return {}

        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
        return {}

    def _save(self) -> None:
        self.storage_path.write_text(json.dumps(self._users, indent=2, ensure_ascii=False), encoding="utf-8")

    # ------------------------ Public API ------------------------
    def is_admin(self, username: str) -> bool:
        username = username.strip()
        if not username:
            return False

        if self.use_mysql:
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM admins WHERE username=%s LIMIT 1", (username,))
            row = cur.fetchone()
            cur.close()
            return bool(row)

        return username in self._load_admins()

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = os.urandom(16).hex()
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        ).hex()
        return f"{salt}:{digest}"

    @staticmethod
    def generate_password(length: int = 14) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = "".join(secrets.choice(alphabet) for _ in range(length))
            if any(c.islower() for c in password) and any(c.isupper() for c in password) and any(c.isdigit() for c in password):
                return password

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        try:
            salt, digest = stored_hash.split(":", 1)
        except ValueError:
            return False
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        ).hex()
        return computed == digest

    def register_user(self, username: str, password: str | None = None) -> bool:
        username = username.strip()
        if not username:
            return False

        password_to_store = password if password else self.generate_password()
        self.last_generated_password = password_to_store
        password_hash = self._hash_password(password_to_store)

        if self.use_mysql:
            conn = get_mysql_connection()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
                return True
            except Exception:
                # likely duplicate key
                return False
            finally:
                cur.close()

        # JSON fallback
        if username in self._users:
            return False
        self._users[username] = password_hash
        self._save()
        return True

    def authenticate(self, username: str, password: str) -> bool:
        username = username.strip()
        if not username:
            return False

        if self.use_mysql:
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute("SELECT password_hash FROM users WHERE username=%s LIMIT 1", (username,))
            row = cur.fetchone()
            cur.close()
            if not row:
                return False
            return self._verify_password(password, row[0])

        stored_hash = self._users.get(username)
        if not stored_hash:
            return False
        return self._verify_password(password, stored_hash)

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        username = username.strip()
        if not username or not old_password or not new_password:
            return False

        if self.use_mysql:
            # verify old
            if not self.authenticate(username, old_password):
                return False
            new_hash = self._hash_password(new_password)
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET password_hash=%s WHERE username=%s",
                (new_hash, username),
            )
            affected = cur.rowcount
            cur.close()
            return affected > 0

        stored_hash = self._users.get(username)
        if not stored_hash or not self._verify_password(old_password, stored_hash):
            return False

        self._users[username] = self._hash_password(new_password)
        self._save()
        return True

    # ------------------------ Migration helpers (optional) ------------------------
    def migrate_from_json_if_possible(self) -> None:
        """Best-effort: import existing JSON users/admins into MySQL."""
        if not self.use_mysql:
            return

        # Load json data
        users = self._load() if self.storage_path.exists() else {}
        admins = self._load_admins() if self.admins_path.exists() else set()

        if not users:
            return

        conn = get_mysql_connection()
        cur = conn.cursor()
        # Upsert users
        for username, password_hash in users.items():
            try:
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s) ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash)",
                    (username, password_hash),
                )
            except Exception:
                continue

        # Upsert admins
        for username in admins:
            try:
                cur.execute(
                    "INSERT INTO admins (username) VALUES (%s) ON DUPLICATE KEY UPDATE username=VALUES(username)",
                    (username,),
                )
            except Exception:
                continue

        cur.close()

