CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE mood (
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    mood_1 INTEGER,
    mood_2 INTEGER,
    mood_3 INTEGER,
    sleep INTEGER,
    health INTEGER,
    work INTEGER,
    remarks TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    PRIMARY KEY (user_id, date)
);