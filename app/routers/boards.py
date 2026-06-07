from fastapi import APIRouter, Depends
from pydantic import BaseModel
from database import get_connection
from auth_utils import get_current_user

router = APIRouter(prefix="/boards", tags=["boards"])

class BoardCreate(BaseModel):
    title: str
    category: str

@router.post("")
def create_board(board: BoardCreate, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO boards (name, title, category, user_id)
            VALUES (%s, %s, %s, %s) RETURNING *
        """, (board.title, board.title, board.category, current_user["user_id"]))
        new_board = cur.fetchone()
        conn.commit()
    return new_board

@router.get("")
def get_boards(current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM boards WHERE user_id = %s", (current_user["user_id"],))
        return cur.fetchall()
