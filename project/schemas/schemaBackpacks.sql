CREATE TABLE backpacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    storage_name TEXT,
    storage_type TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, storage_name)
);
CREATE INDEX idx_user_id ON backpacks (user_id);
CREATE INDEX idx_storage_name ON backpacks (storage_name);
CREATE INDEX idx_storage_type ON backpacks (storage_type);
CREATE INDEX idx_content ON backpacks (content);


ALTER TABLE backpacks ADD COLUMN location TEXT;
ALTER TABLE backpacks ADD COLUMN use TEXT;

CREATE INDEX idx_location ON backpacks (location);
CREATE INDEX idx_use ON backpacks (use);
