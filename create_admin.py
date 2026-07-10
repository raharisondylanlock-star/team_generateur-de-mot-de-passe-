"""
Script de creation du premier compte administrateur.
A lancer une seule fois (ou pour ajouter un admin manuellement) :
    python create_admin.py
"""
import json
import sys
from pathlib import Path
from getpass import getpass

sys.path.insert(0, str(Path(__file__).resolve().parent))

from security.auth_service import AuthService


def main():
    auth = AuthService()

    username = input("Nom d'utilisateur admin : ").strip()
    if not username:
        print("Nom d'utilisateur requis.")
        return

    if username in auth._users:
        print(f"'{username}' existe deja dans users.json, on le passe juste admin.")
    else:
        password = getpass("Mot de passe (vide = genere automatiquement) : ").strip() or None
        if not auth.register_user(username, password):
            print("Echec de la creation du compte.")
            return
        if password is None:
            print(f"Mot de passe genere : {auth.last_generated_password}")

    admins = auth._load_admins()
    if username in admins:
        print(f"'{username}' est deja administrateur.")
        return

    admins.add(username)
    auth.admins_path.write_text(json.dumps(sorted(admins), indent=2), encoding="utf-8")
    print(f"'{username}' est maintenant administrateur. Connecte-toi avec ce compte.")


if __name__ == "__main__":
    main()
