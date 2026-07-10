# TODO - MySQL migration

## Terminé
- Mise en place d'une couche MySQL (`database/mysql_client.py`) avec création automatique des tables.
- Ajout du schéma SQL de référence (`database/schema_mysql.sql`).
- Migration côté `AuthService` et `PasswordService` :
  - si MySQL est configuré → stockage MySQL
  - sinon → fallback JSON (compatibilité).
- Dépendance `mysql-connector-python` ajoutée dans `requirements.txt`.
- Ajout de tests : passage réussi de `python -m unittest discover -s tests -p "test_*.py" -q`.

## À faire (optionnel)
- Migration/transfer explicite des fichiers JSON existants vers MySQL (via `AuthService.migrate_from_json_if_possible()` + script dédié).
- Mettre à jour `create_admin.py` et `ui/admin_panel.py` pour gérer la liste des admins via MySQL uniquement quand MySQL est actif.

