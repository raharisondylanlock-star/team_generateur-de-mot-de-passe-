-- MySQL schema for password-manager

CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(255) PRIMARY KEY,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS admins (
    username VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_admin_user FOREIGN KEY (username) REFERENCES users(username)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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

