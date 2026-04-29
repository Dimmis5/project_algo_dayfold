import time
from models import DayfoldGraph
from visualizer import Neo4jVisualizer

def run_app():
    net = DayfoldGraph()
    
    #  Step 1 : Create users, boards and pins
    print("Step 1")

    alice = net.add_user(1, "Alice")
    bob = net.add_user(2, "Bob")
    charlie = net.add_user(3, "Charlie")
    david = net.add_user(4, "David")
    
    board_deco = net.add_board_to_user(1, 101, "Mon Salon Scandinave", "Décoration")
    if board_deco:
        net.add_pin_to_board(board_deco, 501, "Photo Canape Bleu")
        net.add_pin_to_board(board_deco, 502, "Lampe Vintage 1950")

    board_tech = net.add_board_to_user(2, 102, "Setup Gaming 2024", "Tech")
    if board_tech:
        net.add_pin_to_board(board_tech, 503, "Carte Graphique RTX 4090")

    # Step 2 : Create friendships and test the friend suggestion algorithm
    print("\nStep 2")
    
    net.add_friendship(1, 2) 
    net.add_friendship(2, 3) 
    net.add_friendship(3, 4) 

    suggs = net.suggest_friends(1)
    print(f"RESULT ALGO : The suggestions for Alice are : {suggs}")


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