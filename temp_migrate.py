import os
import psycopg2

def migrate():
    try:
        conn = psycopg2.connect("postgresql://postgres:password123@localhost:5432/dayfold")
        cur = conn.cursor()
        print("Ensuring pin_saves table exists...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pin_saves (
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                pin_id  INTEGER REFERENCES pins(id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, pin_id)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
