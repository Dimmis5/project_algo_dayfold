import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        os.getenv("POSTGRES_URI", "postgresql://postgres:password123@postgres:5432/dayfold"),
        cursor_factory=RealDictCursor
    )