from typing import List

from database.base import db_get

tables_list: List[str] = [
    """
    CREATE TABLE IF NOT EXISTS ip_adresses(
        id SERIAL PRIMARY KEY,
        ip_adress INET NOT NULL UNIQUE,
        timezone VARCHAR(48),
        provider VARCHAR(128),
        country VARCHAR(64),
        region VARCHAR(128),
        city VARCHAR(128),
        latitude NUMERIC(10,7),
        longitude NUMERIC(10,7),
        is_proxy BOOLEAN DEFAULT FALSE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        name VARCHAR(32) NOT NULL,
        email VARCHAR(256),
        password VARCHAR(60) NOT NULL,
        role VARCHAR(8) DEFAULT 'consumer',
        ip INTEGER UNIQUE NOT NULL REFERENCES ip_adresses(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS urls(
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        original_url VARCHAR(2048) NOT NULL,
        short_code VARCHAR(16) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
        password VARCHAR(60),
        valid_from TIME, valid_until TIME,
        allow_proxy BOOLEAN DEFAULT TRUE,
        UNIQUE (user_id, original_url)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS clicks(
        id SERIAL PRIMARY KEY,
        url_id INTEGER NOT NULL REFERENCES urls(id),
        clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_agent VARCHAR(1024),
        ip INTEGER NOT NULL REFERENCES ip_adresses(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS api_keys(
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
        key VARCHAR(64) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
        is_active BOOLEAN DEFAULT TRUE
    )
    """,
]


async def init_tables():
    pool = await db_get()
    async with pool.acquire() as conn:
        for table in tables_list:
            print(await conn.execute(table))
