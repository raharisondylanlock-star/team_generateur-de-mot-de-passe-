import json
import secrets
import string
from pathlib import Path
from typing import Dict, List
import uuid

from cryptography.fernet import Fernet, InvalidToken

try:
    from mysql_client import get_mysql_connection, ensure_schema
except Exception:
    get_mysql_connection = None
    ensure_schema = None



class PasswordService:
    """Gère le stockage chiffré des mots de passe des utilisateurs.

    - Si MySQL est activé/configuré, on stocke les entrées dans la table passwords.
    - Sinon, on garde le stockage JSON legacy.

    Le chiffrement Fernet reste identique au code existant.
    """

    def __init__(self, storage_path: str | None = None, key_path: str | None = None, use_mysql: bool | None = None):
        if storage_path is None:
            storage_path = Path(__file__).resolve().parents[1] / "database" / "passwords.json"
        if key_path is None:
            key_path = Path(storage_path).resolve().parent / "secret.key"

        self.storage_path = Path(storage_path)
        self.key_path = Path(key_path)

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.key_path.parent.mkdir(parents=True, exist_ok=True)

        if use_mysql is None:
            import os
            use_mysql = bool(os.getenv("MYSQL_HOST") or os.getenv("MYSQL_DATABASE") or os.getenv("MYSQL_USER"))

        self.use_mysql = bool(use_mysql)

        self._fernet = Fernet(self._load_or_create_key())

        self._data: Dict[str, List[Dict[str, str]]] = {}
        if self.use_mysql:
            try:
                ensure_schema()
            except Exception:
                self.use_mysql = False

        if not self.use_mysql:
            self._data = self._load()

    def _load_or_create_key(self) -> bytes:
        if self.key_path.exists():
            return self.key_path.read_bytes()
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)
        return key

    def _encrypt(self, plain_password: str) -> str:
        return self._fernet.encrypt(plain_password.encode("utf-8")).decode("utf-8")

    def _decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")
        except (InvalidToken, ValueError):
            return token

    # ---------------------- Legacy JSON ----------------------
    def _load(self) -> Dict[str, List[Dict[str, str]]]:
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")
            return {}

        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            return {}

        if isinstance(data, dict):
            return {
                str(username): [
                    {
                        "id": str(entry.get("id", uuid.uuid4().hex)),
                        "site": str(entry.get("site", "")),
                        "username": str(entry.get("username", "")),
                        "password": self._decrypt(str(entry.get("password", ""))),
                    }
                    for entry in entries
                    if isinstance(entries, list)
                    for entry in entries
                ]
                for username, entries in data.items()
                if isinstance(entries, list)
            }
        return {}

    def _save(self) -> None:
        encrypted = {
            username: [
                {**entry, "password": self._encrypt(entry["password"])}
                for entry in entries
            ]
            for username, entries in self._data.items()
        }
        self.storage_path.write_text(json.dumps(encrypted, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------------- Generator ----------------------
    @staticmethod
    def generate_password(
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
    ) -> str:
        length = max(4, int(length))

        pools = []
        if use_lower:
            pools.append(string.ascii_lowercase)
        if use_upper:
            pools.append(string.ascii_uppercase)
        if use_digits:
            pools.append(string.digits)
        if use_symbols:
            pools.append("!@#$%^&*()-_=+[]{}")

        if not pools:
            pools = [string.ascii_lowercase]

        alphabet = "".join(pools)

        while True:
            password = "".join(secrets.choice(alphabet) for _ in range(length))
            if all(any(c in pool for c in password) for pool in pools):
                return password

    # ---------------------- CRUD ----------------------
    def add_password(self, username: str, site: str, account_username: str, password: str) -> str:
        username = username.strip()
        entry_id = uuid.uuid4().hex

        if self.use_mysql:
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO passwords (id, username, site, account_username, password_enc) VALUES (%s,%s,%s,%s,%s)",
                (entry_id, username, site.strip(), account_username.strip(), self._encrypt(password)),
            )
            cur.close()
            return entry_id

        entry = {
            "id": entry_id,
            "site": site.strip(),
            "username": account_username.strip(),
            "password": password,
        }
        self._data.setdefault(username, []).append(entry)
        self._save()
        return entry_id

    def list_passwords(self, username: str) -> List[Dict[str, str]]:
        username = username.strip()
        if self.use_mysql:
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, site, account_username, password_enc FROM passwords WHERE username=%s ORDER BY created_at DESC",
                (username,),
            )
            rows = cur.fetchall() or []
            cur.close()
            out: List[Dict[str, str]] = []
            for row in rows:
                out.append(
                    {
                        "id": str(row[0]),
                        "site": str(row[1]),
                        "username": str(row[2]),
                        "password": self._decrypt(str(row[3])),
                    }
                )
            return out

        return list(self._data.get(username, []))

    def update_password(self, username: str, entry_id: str, site: str, account_username: str, password: str) -> bool:
        username = username.strip()

        if self.use_mysql:
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE passwords SET site=%s, account_username=%s, password_enc=%s WHERE id=%s AND username=%s",
                (site.strip(), account_username.strip(), self._encrypt(password), entry_id, username),
            )
            affected = cur.rowcount
            cur.close()
            return affected > 0

        entries = self._data.get(username, [])
        for entry in entries:
            if entry.get("id") == entry_id:
                entry["site"] = site.strip()
                entry["username"] = account_username.strip()
                entry["password"] = password
                self._save()
                return True
        return False

    def delete_password(self, username: str, entry_id: str) -> bool:
        username = username.strip()

        if self.use_mysql:
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM passwords WHERE id=%s AND username=%s", (entry_id, username))
            affected = cur.rowcount
            cur.close()
            return affected > 0

        entries = self._data.get(username, [])
        filtered = [entry for entry in entries if entry.get("id") != entry_id]
        if len(filtered) == len(entries):
            return False
        self._data[username] = filtered
        self._save()
        return True

