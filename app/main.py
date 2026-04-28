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

    print("\nTest")
    suggs = net.suggest_friends(1)
    print(f"For Alice : {suggs}") 

    viz = Neo4jVisualizer()
    max_retries = 10
    for i in range(max_retries):
        try:
            viz.driver.verify_connectivity()
            viz.sync_graph(net)
            viz.close() 
            break
        except:
            time.sleep(5)

if __name__ == "__main__":
    run_app()