import time
from models import DayfoldGraph, CategoryNode
from algorithms.bfs_suggest_friends import suggest_friends
from algorithms.feed import build_feed, anti_scroll_gate
from algorithms.category_tree import display_hierarchy, find_category
from algorithms.louvain import louvain
from algorithms.PPR import PersonalizedPageRank, FeedBuilder, build_topic_teleport_set, build_graph_from_dayfold
from visualizer import Neo4jVisualizer
from louvain.louvebetter import louvain as louvain_better

def run_app():
    net = DayfoldGraph()
    print(net)
    print(net.__dict__)
    print("Step 1: Building the Category Tree")
    
    root_cat = CategoryNode(0, "All Categories")

    cat_decor = CategoryNode(1, "Home Decor")
    cat_scand = CategoryNode(11, "Scandinavian")
    cat_indus = CategoryNode(12, "Industrial")
    cat_decor.add_child(cat_scand)
    cat_decor.add_child(cat_indus)
    
    cat_tech = CategoryNode(2, "Technology")
    cat_gaming = CategoryNode(21, "Gaming")
    cat_office = CategoryNode(22, "Office")
    cat_tech.add_child(cat_gaming)
    cat_tech.add_child(cat_office)
    
    cat_art = CategoryNode(3, "Art")
    cat_digital = CategoryNode(31, "Digital Art")
    cat_trad = CategoryNode(32, "Watercolor")
    cat_art.add_child(cat_digital)
    cat_art.add_child(cat_trad)
    
    root_cat.add_child(cat_decor)
    root_cat.add_child(cat_tech)
    root_cat.add_child(cat_art)

    display_hierarchy(root_cat)

    print("\nStep 2: Creating Users, Boards and Pins")

    alice   = net.add_user(1, "Alice")
    bob     = net.add_user(2, "Bob")
    charlie = net.add_user(3, "Charlie")
    david   = net.add_user(4, "David")
    emma    = net.add_user(5, "Emma")
    lucas   = net.add_user(6, "Lucas")

    board_deco = net.add_board_to_user(1, 101, "My Scandinavian Living Room", cat_scand)
    if board_deco:
        net.add_pin_to_board(board_deco, 501, "Blue Sofa Photo")
        net.add_pin_to_board(board_deco, 502, "1950s Vintage Lamp")

    board_tech = net.add_board_to_user(2, 102, "Gaming Setup 2024", cat_gaming)
    if board_tech:
        net.add_pin_to_board(board_tech, 504, "RTX 4090 Graphics Card")

    board_deco2 = net.add_board_to_user(3, 103, "Living Room Inspiration", cat_decor)
    if board_deco2:
        net.add_pin_to_board(board_deco2, 507, "Berber Rug")

    board_tech2 = net.add_board_to_user(4, 104, "Home Office Setup", cat_office)
    if board_tech2:
        net.add_pin_to_board(board_tech2, 510, "Electric Standing Desk")

    board_art = net.add_board_to_user(5, 106, "World Watercolors", cat_trad)
    if board_art:
        net.add_pin_to_board(board_art, 514, "Japanese Landscape")

    board_art2 = net.add_board_to_user(6, 108, "Digital Art", cat_digital)
    if board_art2:
        net.add_pin_to_board(board_art2, 519, "Cyberpunk Illustration")

    # Communauté 1 : Alice, Bob, Charlie
    net.add_friendship(1, 2)
    net.add_friendship(2, 1)
    net.add_friendship(2, 3)
    net.add_friendship(3, 2)

    # Communauté 2 : Emma, Lucas, David
    net.add_friendship(5, 6)
    net.add_friendship(6, 5)
    net.add_friendship(4, 5)
    net.add_friendship(5, 4)

    net.add_friendship(1, 5)

    # Interactions utilisateur compatibles avec Neo4j et Louvain
    net.like_pin(1, 501)
    net.like_pin(2, 501)
    net.save_pin(3, 501)
    net.share_pin(2, 502)

    net.like_pin(4, 514)
    net.save_pin(5, 514)
    net.share_pin(6, 519)
    net.like_pin(1, 514)

    
    print("\nStep 3: Feed Engine & Anti-scroll Gate")

    user_feed = build_feed(net, 1, daily_limit=10)
    print(f"Feed for Alice ({len(user_feed)} pins): {[p.title for p in user_feed]}")

    status_ok = anti_scroll_gate(user_feed, pins_seen=3, daily_limit=10)
    print(f"Anti-scroll (3 seen)  : {status_ok['message']}")

    status_locked = anti_scroll_gate(user_feed, pins_seen=10, daily_limit=10)
    print(f"Anti-scroll (10 seen) : {status_locked['message']}")

    print("\nStep 4: Friend Suggestions (BFS)")

    suggestions = suggest_friends(net, 1)
    print(f"ALGO RESULT: Suggestions for Alice: {suggestions}")

    print("\nStep 5: Community Detection (Louvain)")
    
    louvain_result = louvain_better(net)
    communities = {}
    if louvain_result:
        for comm_id, user_ids in louvain_result.items():
            for user_id in user_ids:
                communities[user_id] = comm_id

    for user_id, comm_id in communities.items():
        username = net.users[user_id].username
        print(f"  {username} -> Community {comm_id}")

    print("\nStep 6: Personalized PageRank Feed")

    ppr_graph = build_graph_from_dayfold(net)
    ppr = PersonalizedPageRank(ppr_graph)
    feed_builder = FeedBuilder(ppr_graph, ppr)

    teleport = build_topic_teleport_set(ppr_graph, "1")
    ppr_feed = feed_builder.build_feed(
        user_id="1",
        seen_pins=set(),
        feed_size=10,
        teleport_set=teleport
    )

    print(f"  Followed   : {ppr_feed['followed']}")
    print(f"  Discovery  : {ppr_feed['discovery']}")
    print(f"  Serendipity: {ppr_feed['serendipity']}")

    # Neo4j Sync
    print("\nConnecting to Neo4j for Visualization")
    viz = Neo4jVisualizer()
    
    max_retries = 15
    for i in range(max_retries):
        try:
            viz.sync_graph(net, communities=communities)
            viz.close()
            print("Success: Graph synchronized! Check the Neo4j browser.")
            break
        except Exception as e:
            print(f"Neo4j not ready yet (Trial {i+1}/{max_retries})...")
            time.sleep(5)
    else:
        print("Error: Could not connect to Neo4j.")

if __name__ == "__main__":
    run_app()
