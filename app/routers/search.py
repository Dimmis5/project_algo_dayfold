from fastapi import APIRouter, Depends
from database import get_connection
from auth_utils import get_current_user

router = APIRouter(tags=["search"])

@router.get("/search")
def search_pins(q: str, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, b.category, b.title as board_title
            FROM pins p
            JOIN boards b ON p.board_id = b.id
            WHERE p.title ILIKE %s OR b.category ILIKE %s
            ORDER BY p.created_at DESC
        """, (f"%{q}%", f"%{q}%"))
        results = cur.fetchall()
    return results
