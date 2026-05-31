import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def run_migration():
    if not DATABASE_URL:
        print("DATABASE_URL is not set!")
        return

    print("Connecting to database...")
    try:
        with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Add github_username column if it doesn't exist
                print("Adding github_username column to users table...")
                cur.execute("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS github_username VARCHAR(255);
                """)
                
                # Make the existing admin user own the current repo's PRs
                # Assuming the existing admin user is 'Shaharyar2442'
                print("Setting github_username for existing admin user...")
                cur.execute("""
                    UPDATE users 
                    SET github_username = 'Shaharyar2442' 
                    WHERE username = 'Shaharyar2442' AND github_username IS NULL;
                """)
                
                print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    run_migration()
