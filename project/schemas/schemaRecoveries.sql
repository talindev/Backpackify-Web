CREATE TABLE recoveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    token TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, token),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_token ON recoveries (token);
