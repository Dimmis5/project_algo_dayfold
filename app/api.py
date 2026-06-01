from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import shutil
import os
from database import get_connection
from models import DayfoldGraph
from algorithms.bfs_suggest_friends import suggest_friends
from algorithms.feed import build_feed, anti_scroll_gate
from algorithms.louvain import louvain
from algorithms.PPR import PersonalizedPageRank, FeedBuilder, build_topic_teleport_set, build_graph_from_dayfold
from visualizer import Neo4jVisualizer
import random

app = FastAPI()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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
        cur.execute("SELECT id FROM users WHERE email = %s OR username = %s", (user.email, user.username))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="L'utilisateur ou l'email existe déjà")
        
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

@app.post("/pins/{pin_id}/like")
def like_pin(pin_id: int, current_user=Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE pins SET likes = likes + 1 WHERE id = %s RETURNING *", (pin_id,))
        pin = cur.fetchone()
        conn.commit()
    return pin

def build_graph_from_postgres(user_id: int) -> DayfoldGraph:
    conn = get_connection()
    graph = DayfoldGraph()
    with conn.cursor() as cur:
        cur.execute("SELECT id, username FROM users")
        for u in cur.fetchall():
            graph.add_user(u["id"], u["username"])

        cur.execute("SELECT follower_id, following_id FROM follows")
        for f in cur.fetchall():
            graph.add_friendship(f["follower_id"], f["following_id"])

        cur.execute("SELECT id, title, category, user_id FROM boards")
        for b in cur.fetchall():
            graph.add_board_to_user(b["user_id"], b["id"], b["title"], b["category"])

        cur.execute("SELECT id, title, likes, board_id, image_url FROM pins")
        for p in cur.fetchall():
            for uid, user in graph.users.items():
                for board in user.boards:
                    if board.board_id == p["board_id"]:
                        pin_obj = graph.add_pin_to_board(board, p["id"], p["title"], p["likes"])
                        if hasattr(pin_obj, '__dict__'):
                            pin_obj.image_url = p["image_url"]

    return graph

@app.get("/algo/feed")
def api_feed(current_user=Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    conn = get_connection()
    feed_final = []

    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.* FROM pins p
            JOIN boards b ON p.board_id = b.id
            JOIN follows f ON b.user_id = f.following_id
            WHERE f.follower_id = %s
            ORDER BY p.created_at DESC LIMIT 20
        """, (user_id,))
        feed_final.extend(cur.fetchall())

        cur.execute("""
            SELECT p.* FROM pins p
            JOIN boards b ON p.board_id = b.id
            WHERE b.category IN (SELECT DISTINCT category FROM boards WHERE user_id = %s)
            AND b.user_id != %s
            AND b.user_id NOT IN (SELECT following_id FROM follows WHERE follower_id = %s)
            ORDER BY p.likes DESC LIMIT 12
        """, (user_id, user_id, user_id))
        feed_final.extend(cur.fetchall())


        already_in_ids = [p['id'] for p in feed_final] if feed_final else [0]
        cur.execute("""
            SELECT * FROM pins 
            WHERE id != ALL(%s) 
            ORDER BY RANDOM() LIMIT 10
        """, (already_in_ids,))
        feed_final.extend(cur.fetchall())

    random.shuffle(feed_final)
    
    return {
        "feed": feed_final,
        "message": "" 
    }

@app.get("/algo/suggest-friends")
def api_suggest_friends(current_user=Depends(get_current_user)):
    graph = build_graph_from_postgres(current_user["user_id"])
    suggested_names = suggest_friends(graph, current_user["user_id"])
    
    conn = get_connection()
    suggestions_with_ids = []
    with conn.cursor() as cur:
        for name in suggested_names:
            cur.execute("SELECT id, username FROM users WHERE username = %s", (name,))
            u = cur.fetchone()
            if u:
                suggestions_with_ids.append(u)
    
    return {"suggestions": suggestions_with_ids}
@app.get("/algo/communities")
def api_communities(current_user=Depends(get_current_user)):
    graph = build_graph_from_postgres(current_user["user_id"])
    communities = louvain(graph)
    result = {graph.users[uid].username: comm_id for uid, comm_id in communities.items()}
    return {"communities": result}

@app.get("/algo/ppr-feed")
def api_ppr_feed(current_user=Depends(get_current_user)):
    graph = build_graph_from_postgres(current_user["user_id"])
    ppr_graph = build_graph_from_dayfold(graph)
    ppr = PersonalizedPageRank(ppr_graph)
    feed_builder = FeedBuilder(ppr_graph, ppr)
    teleport = build_topic_teleport_set(ppr_graph, str(current_user["user_id"]))
    return feed_builder.build_feed(str(current_user["user_id"]), set(), 10, teleport)

@app.get("/users/{user_id}/profile")
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

    return {
        "user": dict(user),
        "boards": boards_with_pins,
        "followers": followers,
        "following": following
    }

@app.post("/users/{user_id}/follow")
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

@app.get("/search")
def search(q: str, current_user=Depends(get_current_user)):
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

@app.get("/algo/sync-graph")
def sync_neo4j_with_postgres(current_user=Depends(get_current_user)):
    try:
        graph = build_graph_from_postgres(current_user["user_id"])
        
        viz = Neo4jVisualizer()
        viz.sync_graph(graph)
        viz.close()
        
        return {"status": "success", "message": "Graphe synchronisé avec succès !"}
    except Exception as e:
        print(f"Erreur Synchro Neo4j: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pins/{pin_id}")
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

@app.get("/pins/{pin_id}/related")
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