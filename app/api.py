from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "dayfold-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class BoardCreate(BaseModel):
    title: str
    category: str

class PinCreate(BaseModel):
    title: str
    board_id: int


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



@app.post("/auth/register")
def register(user: UserRegister):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists")
        cur.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s) RETURNING id, username, email, is_admin
        """, (user.username, user.email, hash_password(user.password)))
        new_user = cur.fetchone()
        conn.commit()
    return {"user": new_user, "token": create_token({"user_id": new_user["id"], "is_admin": new_user["is_admin"]})}

@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (form.username,))
        user = cur.fetchone()
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token({"user_id": user["id"], "is_admin": user["is_admin"]}), "token_type": "bearer"}


@app.get("/users/me")
def get_me(current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, username, email, is_admin FROM users WHERE id = %s", (current_user["user_id"],))
        return cur.fetchone()

@app.post("/users/{user_id}/follow")
def follow_user(user_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO follows (follower_id, following_id)
            VALUES (%s, %s) ON CONFLICT DO NOTHING
        """, (current_user["user_id"], user_id))
        conn.commit()
    return {"message": f"Now following user {user_id}"}

@app.get("/users")
def get_users(current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, username, email, is_admin FROM users")
        return cur.fetchall()


@app.post("/boards")
def create_board(board: BoardCreate, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO boards (title, category, user_id)
            VALUES (%s, %s, %s) RETURNING *
        """, (board.title, board.category, current_user["user_id"]))
        new_board = cur.fetchone()
        conn.commit()
    return new_board

@app.get("/boards")
def get_boards(current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM boards WHERE user_id = %s", (current_user["user_id"],))
        return cur.fetchall()


@app.post("/pins")
def create_pin(pin: PinCreate, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM boards WHERE id = %s AND user_id = %s", (pin.board_id, current_user["user_id"]))
        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="Board not found or not yours")
        cur.execute("""
            INSERT INTO pins (title, board_id)
            VALUES (%s, %s) RETURNING *
        """, (pin.title, pin.board_id))
        new_pin = cur.fetchone()
        conn.commit()
    return new_pin

@app.get("/pins/{board_id}")
def get_pins(board_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM pins WHERE board_id = %s", (board_id,))
        return cur.fetchall()

@app.post("/pins/{pin_id}/like")
def like_pin(pin_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE pins SET likes = likes + 1 WHERE id = %s RETURNING *", (pin_id,))
        pin = cur.fetchone()
        conn.commit()
    return pin