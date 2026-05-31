import asyncio
import os
import sys
import psycopg

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_URL

def create_users_table():
    print("Connecting to database to create users table...")
    try:
        with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL
                    )
                """)
                print("Users table created successfully!")
    except Exception as e:
        print(f"Error creating users table: {e}")

if __name__ == "__main__":
    create_users_table()
