CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE UNIQUE INDEX username ON users (username);

ALTER TABLE users ADD COLUMN email TEXT NOT NULL;

CREATE UNIQUE INDEX email ON users (email);
