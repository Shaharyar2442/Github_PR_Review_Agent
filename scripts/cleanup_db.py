import asyncio
import os
import sys
import psycopg

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_URL

def cleanup_thread(thread_id: str):
    print(f"Connecting to database to purge ghost thread: {thread_id}...")
    try:
        with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Delete from LangGraph checkpointer tables
                cur.execute("DELETE FROM checkpoint_writes WHERE thread_id = %s", (thread_id,))
                writes_deleted = cur.rowcount
                
                cur.execute("DELETE FROM checkpoints WHERE thread_id = %s", (thread_id,))
                checkpoints_deleted = cur.rowcount
                
                print(f"Successfully purged {thread_id}!")
                print(f"Deleted {checkpoints_deleted} checkpoints and {writes_deleted} writes.")
    except Exception as e:
        print(f"Error purging thread: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cleanup_db.py <thread_id>")
        print("Example: python cleanup_db.py pr_13")
    else:
        cleanup_thread(sys.argv[1])
