import time
from models import DayfoldGraph
from visualizer import Neo4jVisualizer

def run_app():
    net = DayfoldGraph()
    net.add_user(1, "Alice")
    net.add_user(2, "Bob")
    net.add_user(3, "Charlie")
    net.add_user(4, "David")
    
    net.add_friendship(1, 2)
    net.add_friendship(2, 3)
    net.add_friendship(3, 4)
    net.add_friendship(4, 1)

    print("Tentative de connexion à Neo4j...")
    time.sleep(10) 
    
    try:
        viz = Neo4jVisualizer()
        viz.sync_graph(net)
        viz.close()
        print("Graphe synchronisé avec succès !")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    run_app()