from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from auth_utils import get_current_user
from graph_utils import build_graph_from_postgres
from algorithms.bfs_suggest_friends import suggest_friends
from algorithms.louvain import louvain
from algorithms.PPR import PersonalizedPageRank, FeedBuilder, build_topic_teleport_set, build_graph_from_dayfold
from visualizer import Neo4jVisualizer
import random
from collections import Counter

router = APIRouter(prefix="/algo", tags=["algo"])

def get_community_groups(graph):
    communities = louvain(graph)

    comm_to_users = {}
    for uid, comm_id in communities.items():
        if comm_id not in comm_to_users:
            comm_to_users[comm_id] = []
        comm_to_users[comm_id].append(uid)

    orphans = []
    final_comm_to_users = {}
    for comm_id, uids in comm_to_users.items():
        if len(uids) < 2:
            orphans.extend(uids)
        else:
            final_comm_to_users[str(comm_id)] = uids

    if orphans:
        final_comm_to_users["orphans"] = orphans

    return final_comm_to_users

def get_community_names(graph, community_groups):
    comm_names = {}
    suffixes = ["Lovers", "Squad", "Hub", "Explorers", "Collective", "Addicts", "Club", "Circle"]
    fallbacks = ["Creative Minds", "Trendsetters", "Rising Stars", "Visionaries", "Dayfold Stars"]

    for comm_id, uids in community_groups.items():
        if comm_id == "orphans":
            comm_names[comm_id] = "New Explorers"
            continue

        categories = []
        for uid in uids:
            user = graph.users[uid]
            for board in user.boards:
                if board.category:
                    categories.append(board.category)

        idx = hash(str(comm_id)) % 100
        if categories:
            most_common = Counter(categories).most_common(1)[0][0]
            suffix = suffixes[idx % len(suffixes)]
            comm_names[comm_id] = f"{most_common} {suffix}"
        else:
            name_base = fallbacks[idx % len(fallbacks)]
            comm_names[comm_id] = f"{name_base}"

    return comm_names

@router.get("/feed")
def api_feed(current_user=Depends(get_current_user), page: int = 1):
    user_id = current_user["user_id"]
    page_size = 20
    offset = (page - 1) * page_size

    n_followed = int(page_size * 0.5)
    n_discovery = int(page_size * 0.3)
    n_random = page_size - n_followed - n_discovery

    conn = get_connection()

    with conn.cursor() as cur:
        # 50% 
        cur.execute("""
            SELECT p.*, b.category, u.username as author
            FROM pins p
            JOIN boards b ON p.board_id = b.id
            JOIN users u ON b.user_id = u.id
            JOIN follows f ON b.user_id = f.following_id
            WHERE f.follower_id = %s
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, n_followed, offset))
        followed_pins = [dict(p, feed_type="followed") for p in cur.fetchall()]

        # 30% 
        already_ids = [p['id'] for p in followed_pins] or [0]
        cur.execute("""
            SELECT p.*, b.category, u.username as author
            FROM pins p
            JOIN boards b ON p.board_id = b.id
            JOIN users u ON b.user_id = u.id
            WHERE b.category IN (
                SELECT DISTINCT category FROM boards WHERE user_id = %s
            )
            AND b.user_id != %s
            AND b.user_id NOT IN (SELECT following_id FROM follows WHERE follower_id = %s)
            AND p.id != ALL(%s)
            ORDER BY p.likes DESC, RANDOM()
            LIMIT %s OFFSET %s
        """, (user_id, user_id, user_id, already_ids, n_discovery, offset))
        discovery_pins = [dict(p, feed_type="discovery") for p in cur.fetchall()]

        # 20% 
        already_ids += [p['id'] for p in discovery_pins]
        cur.execute("""
            SELECT p.*, b.category, u.username as author
            FROM pins p
            JOIN boards b ON p.board_id = b.id
            JOIN users u ON b.user_id = u.id
            WHERE p.id != ALL(%s)
            ORDER BY RANDOM()
            LIMIT %s
        """, (already_ids, n_random))
        random_pins = [dict(p, feed_type="random") for p in cur.fetchall()]

        cur.execute("SELECT pin_id FROM pin_likes WHERE user_id = %s", (user_id,))
        liked_ids = [row["pin_id"] for row in cur.fetchall()]

    feed_final = []
    buckets = [followed_pins, discovery_pins, random_pins]
    while any(buckets):
        for bucket in buckets:
            if bucket:
                feed_final.append(bucket.pop(0))

    message = ""
    if page == 1:
        messages = [
            "Crée quelque chose aujourd'hui, même une esquisse.",
            "L'inspiration vient en faisant, pas en scrollant.",
            "Et si tu partageais quelque chose à toi ?",
            "Pause. Respire. Crée.",
        ]
        message = random.choice(messages)

    return {
        "feed": feed_final,
        "liked_ids": liked_ids,
        "message": message,
        "page": page,
        "has_more": len(feed_final) == page_size
    }

@router.get("/suggest-friends")
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

@router.get("/communities")
def api_communities(current_user=Depends(get_current_user)):
    graph = build_graph_from_postgres(current_user["user_id"])
    final_comm_to_users = get_community_groups(graph)
    comm_names = get_community_names(graph, final_comm_to_users)

    result = {}
    for comm_id, uids in final_comm_to_users.items():
        for uid in uids:
            result[graph.users[uid].username] = comm_id
    
    return {
        "communities": result,
        "names": {str(k): v for k, v in comm_names.items()}
    }

@router.get("/communities/{community_id}/pins")
def api_community_pins(community_id: str, current_user=Depends(get_current_user)):
    graph = build_graph_from_postgres(current_user["user_id"])
    community_groups = get_community_groups(graph)
    user_ids = community_groups.get(community_id)

    if not user_ids:
        raise HTTPException(status_code=404, detail="Community not found")

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, b.title as board_title, b.category, u.username as author, u.id as author_id
            FROM pins p
            JOIN boards b ON p.board_id = b.id
            JOIN users u ON b.user_id = u.id
            WHERE b.user_id = ANY(%s)
            ORDER BY p.created_at DESC, p.likes DESC
            LIMIT 60
        """, (user_ids,))
        pins = cur.fetchall()

    return {"community_id": community_id, "pins": pins}

@router.get("/ppr-feed")
def api_ppr_feed(current_user=Depends(get_current_user)):
    graph = build_graph_from_postgres(current_user["user_id"])
    ppr_graph = build_graph_from_dayfold(graph)
    ppr = PersonalizedPageRank(ppr_graph)
    feed_builder = FeedBuilder(ppr_graph, ppr)
    teleport = build_topic_teleport_set(ppr_graph, str(current_user["user_id"]))
    raw_feed = feed_builder.build_feed(str(current_user["user_id"]), set(), 10, teleport)

    # Fetch full pin details for each bucket
    conn = get_connection()
    detailed_feed = {}
    with conn.cursor() as cur:
        for bucket, pin_ids in raw_feed.items():
            if not pin_ids:
                detailed_feed[bucket] = []
                continue
            
            # Convert string IDs back to integers
            int_ids = [int(pid) for pid in pin_ids]
            
            cur.execute("""
                SELECT p.*, b.title as board_title, u.username as author, u.id as author_id
                FROM pins p
                JOIN boards b ON p.board_id = b.id
                JOIN users u ON b.user_id = u.id
                WHERE p.id = ANY(%s)
            """, (int_ids,))
            pins = {p["id"]: dict(p) for p in cur.fetchall()}
            # Reorder pins according to PPR ranking
            detailed_feed[bucket] = [pins[pid] for pid in int_ids if pid in pins]

    return detailed_feed

@router.get("/sync-graph")
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
