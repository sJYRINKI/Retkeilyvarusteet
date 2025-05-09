CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE packs (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    weight INTEGER,
    price INTEGER,
    user_id INTEGER REFERENCES users ON DELETE CASCADE
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    pack_id INTEGER REFERENCES packs ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    comment TEXT
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE pack_classes (
    id INTEGER PRIMARY KEY,
    pack_id INTEGER REFERENCES packs ON DELETE CASCADE,
    title TEXT,
    value TEXT
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    pack_id INTEGER REFERENCES packs ON DELETE CASCADE,
    image BLOB
);
