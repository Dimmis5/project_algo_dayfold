import time
import random
from models import DayfoldGraph, CategoryNode
from algorithms.bfs_suggest_friends import suggest_friends
from algorithms.feed import build_feed, anti_scroll_gate
from algorithms.category_tree import display_hierarchy
from visualizer import Neo4jVisualizer

def run_app():
    net = DayfoldGraph()

    # STEP 1: CATEGORY HIERARCHY (TREES)
    print("--- Step 1: Building the Category Tree ---")
    
    root_cat = CategoryNode(0, "All Categories")

    cat_decor = CategoryNode(1, "Home Decor")
    cat_scand = CategoryNode(11, "Scandinavian")
    cat_decor.add_child(cat_scand)
    
    cat_tech = CategoryNode(2, "Technology")
    cat_gaming = CategoryNode(21, "Gaming")
    cat_tech.add_child(cat_gaming)
    
    cat_art = CategoryNode(3, "Art")
    cat_trad = CategoryNode(32, "Watercolor")
    cat_art.add_child(cat_trad)
    
    root_cat.add_child(cat_decor)
    root_cat.add_child(cat_tech)
    root_cat.add_child(cat_art)

    display_hierarchy(root_cat)

    # STEP 2: DATA MODELING (3 USERS)
    print("\n--- Step 2: Creating 3 Users, Boards and Pins ---")

    alice   = net.add_user(1, "Alice")
    bob     = net.add_user(2, "Bob")
    charlie = net.add_user(3, "Charlie")

    board_alice = net.add_board_to_user(1, 101, "My Nordic Home", cat_scand)
    if board_alice:
        net.add_pin_to_board(board_alice, 501, "White Couch")
        net.add_pin_to_board(board_alice, 502, "Wooden Lamp")

    board_bob = net.add_board_to_user(2, 102, "Gaming Setup", cat_gaming)
    if board_bob:
        net.add_pin_to_board(board_bob, 504, "Mechanical Keyboard")

    board_charlie = net.add_board_to_user(3, 103, "Paintings", cat_trad)
    if board_charlie:
        net.add_pin_to_board(board_charlie, 507, "Blue Ocean Watercolor")


    net.add_friendship(1, 2) 
    net.add_friendship(2, 3) 

    # STEP 3: FEED ENGINE & ANTI-SCROLL
    print("\n--- Step 3: Feed Engine for Alice ---")

    user_feed = build_feed(net, 1, daily_limit=5)
    print(f"Feed for Alice ({len(user_feed)} pins): {[p.title for p in user_feed]}")

    status = anti_scroll_gate(user_feed, pins_seen=2, daily_limit=5)
    print(f"Anti-scroll status (2/5 seen): {status['message']}")

    # STEP 4: RECOMMENDATION ENGINE (BFS)
    print("\n--- Step 4: Friend Suggestions (BFS) ---")

    suggestions = suggest_friends(net, 1)
    print(f"ALGO RESULT: Recommendations for Alice: {suggestions}")

    # NEO4J SYNCHRONIZATION
    print("\n--- Syncing to Neo4j for Visualization ---")
    viz = Neo4jVisualizer()
    
    max_retries = 5
    for i in range(max_retries):
        try:
            viz.sync_graph(net)
            viz.close()
            print("Success: Graph synchronized! View it in the Neo4j browser.")
            break
        except Exception:
            print(f"Neo4j connection trial {i+1}/{max_retries}...")
            time.sleep(3)
    else:
        print("Error: Could not connect to Neo4j.")

if __name__ == "__main__":
    run_app()