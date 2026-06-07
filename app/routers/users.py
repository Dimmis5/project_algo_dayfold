from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from auth_utils import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id::text AS id, username, email FROM users WHERE id = %s",
            (current_user["user_id"],),
        )
        user = cur.fetchone()
        if user:
            user["is_admin"] = False
        return user


@router.get("/search")
def search_users(q: str, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id::text AS id, username, email
            FROM users
            WHERE id != %s
              AND (username ILIKE %s OR email ILIKE %s)
            ORDER BY username
            LIMIT 12
            """,
            (current_user["user_id"], f"%{q}%", f"%{q}%"),
        )
        return {"users": cur.fetchall()}


@router.get("/suggestions")
def friend_suggestions(current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT u.id::text AS id, u.username, u.email, 'friend_of_friend' AS reason
            FROM follows mine
            JOIN follows second_degree ON second_degree.follower_id = mine.following_id
            JOIN users u ON u.id = second_degree.following_id
            WHERE mine.follower_id = %s
              AND u.id != %s
              AND NOT EXISTS (
                  SELECT 1
                  FROM follows existing
                  WHERE existing.follower_id = %s
                    AND existing.following_id = u.id
              )
            ORDER BY u.username
            LIMIT 8
            """,
            (current_user["user_id"], current_user["user_id"], current_user["user_id"]),
        )
        suggestions = cur.fetchall()

        if suggestions:
            return {"suggestions": suggestions}

        cur.execute(
            """
            SELECT u.id::text AS id, u.username, u.email, 'popular' AS reason
            FROM users u
            WHERE u.id != %s
              AND NOT EXISTS (
                  SELECT 1
                  FROM follows existing
                  WHERE existing.follower_id = %s
                    AND existing.following_id = u.id
              )
            ORDER BY (
                SELECT COUNT(*)
                FROM follows f
                WHERE f.following_id = u.id
            ) DESC, u.username
            LIMIT 8
            """,
            (current_user["user_id"], current_user["user_id"]),
        )
        return {"suggestions": cur.fetchall()}


@router.get("/{user_id}/profile")
def get_profile(user_id: str, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id::text AS id, username, email FROM users WHERE id = %s",
            (user_id,),
        )
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouve")
        user["is_admin"] = False

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

        cur.execute(
            "SELECT 1 FROM follows WHERE follower_id = %s AND following_id = %s",
            (current_user["user_id"], user_id),
        )
        is_following = cur.fetchone() is not None

    return {
        "user": dict(user),
        "boards": boards_with_pins,
        "followers": followers,
        "following": following,
        "is_following": is_following,
    }


@router.post("/{user_id}/follow")
def follow_user(user_id: str, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        if user_id == current_user["user_id"]:
            raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous suivre vous-meme")

        cur.execute(
            """
            INSERT INTO follows (follower_id, following_id)
            VALUES (%s, %s) ON CONFLICT DO NOTHING
            """,
            (current_user["user_id"], user_id),
        )
        conn.commit()
    return {"message": f"Vous suivez maintenant l'utilisateur {user_id}"}
