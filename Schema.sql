CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    full_name VARCHAR(255)
);

CREATE TABLE threads (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255),
    last_updated DATETIME
);

CREATE TABLE messages (
    id VARCHAR(255) PRIMARY KEY,
    thread_id VARCHAR(255),
    user_id BIGINT,
    text TEXT,
    timestamp DATETIME,
    FOREIGN KEY (thread_id) REFERENCES threads(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);