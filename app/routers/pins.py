from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from database import get_connection
from auth_utils import get_current_user
import shutil
import os
from datetime import datetime

router = APIRouter(prefix="/pins", tags=["pins"])

UPLOAD_DIR = "uploads"

@router.post("")
async def create_pin(
    title: str = Form(...), 
    board_id: int = Form(...), 
    file: UploadFile = File(...), 
    current_user=Depends(get_current_user)
):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM boards WHERE id = %s AND user_id = %s", (board_id, current_user["user_id"]))
        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="Board introuvable ou ne vous appartient pas")
        
        filename = f"{datetime.now().timestamp()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        image_url = f"/uploads/{filename}"

        cur.execute("""
            INSERT INTO pins (title, board_id, image_url)
            VALUES (%s, %s, %s) RETURNING *
        """, (title, board_id, image_url))
        new_pin = cur.fetchone()
        conn.commit()
    return new_pin

@router.get("/{pin_id}")
def get_pin(pin_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, b.title as board_title, b.category, u.id as author_id, u.username as author
            FROM pins p
            JOIN boards b ON p.board_id = b.id
            JOIN users u ON b.user_id = u.id
            WHERE p.id = %s
        """, (pin_id,))
        pin = cur.fetchone()
        if not pin:
            raise HTTPException(status_code=404, detail="Pin introuvable")
    return pin

@router.post("/{pin_id}/like")
def like_pin(pin_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pin_likes WHERE user_id = %s AND pin_id = %s",
                    (current_user["user_id"], pin_id))
        already_liked = cur.fetchone()

        if already_liked:
            cur.execute("DELETE FROM pin_likes WHERE user_id = %s AND pin_id = %s",
                        (current_user["user_id"], pin_id))
            cur.execute("UPDATE pins SET likes = GREATEST(likes - 1, 0) WHERE id = %s RETURNING *",
                        (pin_id,))
        else:
            cur.execute("INSERT INTO pin_likes (user_id, pin_id) VALUES (%s, %s)",
                        (current_user["user_id"], pin_id))
            cur.execute("UPDATE pins SET likes = likes + 1 WHERE id = %s RETURNING *",
                        (pin_id,))

        pin = cur.fetchone()
        conn.commit()
    return {"pin": pin, "liked": not already_liked}

@router.post("/{pin_id}/save")
def save_pin(pin_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        # Check if already saved
        cur.execute("SELECT 1 FROM pin_saves WHERE user_id = %s AND pin_id = %s",
                    (current_user["user_id"], pin_id))
        if cur.fetchone():
            return {"message": "Already saved", "saved": True}
        
        cur.execute("INSERT INTO pin_saves (user_id, pin_id) VALUES (%s, %s)",
                    (current_user["user_id"], pin_id))
        conn.commit()
    return {"message": "Saved successfully", "saved": True}

@router.delete("/{pin_id}/save")
def unsave_pin(pin_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM pin_saves WHERE user_id = %s AND pin_id = %s",
                    (current_user["user_id"], pin_id))
        conn.commit()
    return {"message": "Unsaved successfully", "saved": False}

@router.get("/{pin_id}/related")
def get_related_pins(pin_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT category FROM pins p JOIN boards b ON p.board_id = b.id WHERE p.id = %s", (pin_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pin introuvable")
        category = row["category"]

        cur.execute("""
            SELECT p.*, b.category, u.username as author
            FROM pins p
            JOIN boards b ON p.board_id = b.id
            JOIN users u ON b.user_id = u.id
            WHERE b.category = %s AND p.id != %s
            ORDER BY RANDOM()
            LIMIT 20
        """, (category, pin_id))
        related = cur.fetchall()
    return {"related": related}
