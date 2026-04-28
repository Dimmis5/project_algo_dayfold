import time
from neo4j.exceptions import ServiceUnavailable
from models import DayfoldGraph
from visualizer import Neo4jVisualizer

def wait_for_neo4j(max_retries=30, delay=10):
    print("Wait 20s for Neo4j...")
    time.sleep(20)
    for attempt in range(max_retries):
        try:
            viz = Neo4jVisualizer()
            viz.driver.verify_connectivity()
            print("Neo4j ready ")
            return viz
        except Exception as e:
            print(f"Try {attempt + 1}/{max_retries} - Neo4j not ready yet: {e}")
            time.sleep(delay)
    raise RuntimeError("Bug")

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

    viz = wait_for_neo4j()
    viz.sync_graph(net)
    viz.close()
    print("Graphe Succes")

if __name__ == "__main__":
    run_app()