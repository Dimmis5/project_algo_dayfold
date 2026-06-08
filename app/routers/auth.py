from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from database import get_connection
from auth_utils import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
def register(user: UserRegister):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email = %s OR username = %s", (user.email, user.username))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="L'utilisateur ou l'email existe déjà")
        
        cur.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s) RETURNING id::text AS id, username, email
        """, (user.username, user.email, hash_password(user.password)))
        new_user = cur.fetchone()
        conn.commit()
    new_user["is_admin"] = False
    return {"user": new_user, "token": create_token({"user_id": new_user["id"], "is_admin": False})}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (form.username,))
        user = cur.fetchone()
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "access_token": create_token({
            "user_id": str(user["id"]),
            "is_admin": user.get("is_admin", False)
        }),
        "token_type": "bearer"
    }
