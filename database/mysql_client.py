import os
from typing import Optional

import mysql.connector
from mysql.connector.connection import MySQLConnection


def get_mysql_connection() -> MySQLConnection:
    """Create a MySQL connection using environment variables.

    Required env vars:
      - MYSQL_HOST (default: localhost)
      - MYSQL_PORT (default: 3306)
      - MYSQL_USER (default: root)
      - MYSQL_PASSWORD (default: empty)
      - MYSQL_DATABASE (default: password_manager)
    """

    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "password_manager")

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        autocommit=True,
    )


def ensure_schema() -> None:
    """Create tables if they do not exist."""
    conn = get_mysql_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255) PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            username VARCHAR(255) PRIMARY KEY,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_admin_user FOREIGN KEY (username) REFERENCES users(username)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    # passwords are encrypted with Fernet on the client side in PasswordService.
    # We keep the same data shape but store it in MySQL.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS passwords (
            id CHAR(32) PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            site VARCHAR(255) NOT NULL,
            account_username VARCHAR(255) NOT NULL,
            password_enc TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_pw_user FOREIGN KEY (username) REFERENCES users(username)
                ON DELETE CASCADE,
            INDEX idx_pw_username (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    cur.close()

