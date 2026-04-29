import time
import random
from models import DayfoldGraph, CategoryNode
from algorithms.bfs_suggest_friends import suggest_friends
from algorithms.feed import build_feed, anti_scroll_gate
from algorithms.category_tree import display_hierarchy, find_category
from visualizer import Neo4jVisualizer

def run_app():
    net = DayfoldGraph()

    print(" Step 3: Building the Category Tree ")
    
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
    print("\nStep 1: Creating Users, Boards and Pins ")
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

    net.add_friendship(1, 2) 
    net.add_friendship(2, 3) 
    net.add_friendship(3, 4) 
    net.add_friendship(1, 5) 
    net.add_friendship(5, 6) 

    print("\n Step 2: Feed Engine & Anti-scroll Gate ")

    user_feed = build_feed(net, 1, daily_limit=10)
    print(f"Feed generated for Alice ({len(user_feed)} pins): {[p.title for p in user_feed]}")

    status_ok = anti_scroll_gate(user_feed, pins_seen=3, daily_limit=10)
    print(f"Anti-scroll Status (3 seen): {status_ok['message']}")
    
    status_locked = anti_scroll_gate(user_feed, pins_seen=10, daily_limit=10)
    print(f"Anti-scroll Status (10 seen): {status_locked['message']}")



    print("\n Step 4: Friend Suggestions (BFS Algorithm)")

    suggestions = suggest_friends(net, 1)
    print(f"ALGO RESULT: The suggestions for Alice are: {suggestions}")

    print("\n Connecting to Neo4j for Visualization ")
    viz = Neo4jVisualizer()
    
    max_retries = 15
    for i in range(max_retries):
        try:
            viz.sync_graph(net)
            viz.close()
            print("Success: Graph synchronized! Check the Neo4j browser interface.")
            break
        except Exception as e:
            print(f"Neo4j is not ready yet (Trial {i+1}/{max_retries})...")
            time.sleep(5)
    else:
        print("Error: Could not connect to Neo4j after multiple attempts.")

if __name__ == "__main__":
    run_app()