from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from auth_utils import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, username, email, is_admin FROM users WHERE id = %s", (current_user["user_id"],))
        return cur.fetchone()

@router.get("/{user_id}/profile")
def get_profile(user_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, username, email, is_admin FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user: raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        cur.execute("SELECT * FROM boards WHERE user_id = %s", (user_id,))
        boards = cur.fetchall()

        boards_with_pins = []
        for board in boards:
            cur.execute("SELECT * FROM pins WHERE board_id = %s", (board["id"],))
            pins = cur.fetchall()
            boards_with_pins.append({**board, "pins": list(pins)})

        cur.execute("SELECT COUNT(*) as count FROM follows WHERE following_id = %s", (user_id,))
        followers = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) as count FROM follows WHERE follower_id = %s", (user_id,))
        following = cur.fetchone()["count"]

        cur.execute("SELECT 1 FROM follows WHERE follower_id = %s AND following_id = %s", (current_user["user_id"], user_id))
        is_following = cur.fetchone() is not None

    return {
        "user": dict(user),
        "boards": boards_with_pins,
        "followers": followers,
        "following": following,
        "is_following": is_following
    }

@router.post("/{user_id}/follow")
def follow_user(user_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        if user_id == current_user["user_id"]:
            raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous suivre vous-même")
            
        cur.execute("""
            INSERT INTO follows (follower_id, following_id)
            VALUES (%s, %s) ON CONFLICT DO NOTHING
        """, (current_user["user_id"], user_id))
        conn.commit()
    return {"message": f"Vous suivez maintenant l'utilisateur {user_id}"}

@router.get("/{user_id}/saved")
def get_saved_pins(user_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, b.title as board_title, u.username as author, u.id as author_id
            FROM pins p
            JOIN pin_saves ps ON p.id = ps.pin_id
            JOIN boards b ON p.board_id = b.id
            JOIN users u ON b.user_id = u.id
            WHERE ps.user_id = %s
            ORDER BY p.created_at DESC
        """, (user_id,))
        saved_pins = cur.fetchall()
    return {"saved_pins": saved_pins}
