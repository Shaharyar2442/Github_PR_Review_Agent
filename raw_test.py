import asyncio
from psycopg_pool import AsyncConnectionPool
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_URL

async def check_db():
    print(f"Connecting to {DATABASE_URL}...")
    async with AsyncConnectionPool(DATABASE_URL, max_size=5) as pool:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT thread_id, checkpoint_id FROM checkpoints")
                rows = await cur.fetchall()
                print(f"Total checkpoints: {len(rows)}")
                for row in rows:
                    print(row)

                await cur.execute("SELECT thread_id, task_id, channel FROM checkpoint_writes")
                writes = await cur.fetchall()
                print(f"Total checkpoint writes: {len(writes)}")

if __name__ == "__main__":
    asyncio.run(check_db())
