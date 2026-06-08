CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS boards (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pins (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    likes INTEGER DEFAULT 0,
    image_url TEXT, 
    board_id INTEGER REFERENCES boards(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS follows (
    follower_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    following_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (follower_id, following_id)
);

CREATE TABLE IF NOT EXISTS pin_likes (

    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    pin_id  INTEGER REFERENCES pins(id) ON DELETE CASCADE,

    PRIMARY KEY (user_id, pin_id)

);



CREATE TABLE IF NOT EXISTS pin_saves (

    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    pin_id  INTEGER REFERENCES pins(id) ON DELETE CASCADE,

    PRIMARY KEY (user_id, pin_id)

);
