from database import get_connection
from models import DayfoldGraph

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
