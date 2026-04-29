import time
from models import DayfoldGraph
from algorithms.bfs_suggest_friends import suggest_friends
from algorithms.feed import build_feed, anti_scroll_gate
from visualizer import Neo4jVisualizer

def run_app():
    net = DayfoldGraph()
    
    # Step 1 : Create users, boards and pins
    print("Step 1")

    alice   = net.add_user(1, "Alice")
    bob     = net.add_user(2, "Bob")
    charlie = net.add_user(3, "Charlie")
    david   = net.add_user(4, "David")
    emma    = net.add_user(5, "Emma")
    lucas   = net.add_user(6, "Lucas")

    # Alice - Décoration
    board_deco = net.add_board_to_user(1, 101, "Mon Salon Scandinave", "Décoration")
    if board_deco:
        net.add_pin_to_board(board_deco, 501, "Photo Canape Bleu")
        net.add_pin_to_board(board_deco, 502, "Lampe Vintage 1950")
        net.add_pin_to_board(board_deco, 503, "Etagere Industrielle")

    # Bob - Tech
    board_tech = net.add_board_to_user(2, 102, "Setup Gaming 2024", "Tech")
    if board_tech:
        net.add_pin_to_board(board_tech, 504, "Carte Graphique RTX 4090")
        net.add_pin_to_board(board_tech, 505, "Clavier Mecanique RGB")
        net.add_pin_to_board(board_tech, 506, "Ecran Ultrawide 4K")

    # Charlie - Décoration
    board_deco2 = net.add_board_to_user(3, 103, "Inspiration Salon", "Décoration")
    if board_deco2:
        net.add_pin_to_board(board_deco2, 507, "Tapis Berbere")
        net.add_pin_to_board(board_deco2, 508, "Plante Monstera")
        net.add_pin_to_board(board_deco2, 509, "Miroir Rotin")

    # David - Tech + Décoration
    board_tech2 = net.add_board_to_user(4, 104, "Home Office Setup", "Tech")
    if board_tech2:
        net.add_pin_to_board(board_tech2, 510, "Bureau Debout Electrique")
        net.add_pin_to_board(board_tech2, 511, "Webcam 4K")

    board_deco3 = net.add_board_to_user(4, 105, "Chambre Cosy", "Décoration")
    if board_deco3:
        net.add_pin_to_board(board_deco3, 512, "Guirlande Lumineuse")
        net.add_pin_to_board(board_deco3, 513, "Tete de Lit Velours")

    # Emma - Art
    board_art = net.add_board_to_user(5, 106, "Aquarelles du Monde", "Art")
    if board_art:
        net.add_pin_to_board(board_art, 514, "Paysage Japonais")
        net.add_pin_to_board(board_art, 515, "Portrait Abstrait")
        net.add_pin_to_board(board_art, 516, "Nature Morte Moderne")

    # Lucas - Tech + Art
    board_tech3 = net.add_board_to_user(6, 107, "Gadgets 2024", "Tech")
    if board_tech3:
        net.add_pin_to_board(board_tech3, 517, "Drone FPV Racing")
        net.add_pin_to_board(board_tech3, 518, "Imprimante 3D Resine")

    board_art2 = net.add_board_to_user(6, 108, "Digital Art", "Art")
    if board_art2:
        net.add_pin_to_board(board_art2, 519, "Illustration Cyberpunk")
        net.add_pin_to_board(board_art2, 520, "Pixel Art Retro")

    net.add_friendship(1, 2)
    net.add_friendship(2, 3)
    net.add_friendship(3, 4)
    net.add_friendship(1, 5)
    net.add_friendship(5, 6)

    # Step 2 : Feed & Anti-scroll
    print("\nStep 2 - Feed & Anti-scroll")

    feed = build_feed(net, 1, daily_limit=10)
    print(f"Feed for Alice ({len(feed)} pins): {[p.title for p in feed]}")

    # result_ok = anti_scroll_gate(feed, pins_seen=3)
    # print(f"Anti-scroll (3 seen)  : {result_ok['message']}")

    # result_locked = anti_scroll_gate(feed, pins_seen=10)
    # print(f"Anti-scroll (10 seen) : {result_locked['message']}")

    # Step 4 : Friend suggestions (BFS)
    print("\nStep 4 - Friend suggestions")

    suggs = suggest_friends(net, 1)
    print(f"ALGO RESULT : The suggestions for Alice are : {suggs}")

    # Sync to Neo4j
    print("\nNeo4j")
    viz = Neo4jVisualizer()
    
    max_retries = 15
    for i in range(max_retries):
        try:
            viz.sync_graph(net)
            viz.close()
            print("Complete graph successfully synchronized! Check out Neo4j")
            break
        except Exception as e:
            print(f"Neo4j is not yet ready (Trial {i+1}/{max_retries})...")
            time.sleep(5)
    else:
        print("Error: Unable to connect to Neo4j")

if __name__ == "__main__":
    run_app()