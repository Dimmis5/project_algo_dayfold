import os
from neo4j import GraphDatabase

class Neo4jVisualizer:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def sync_graph(self, dayfold_graph):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            
            for u_id, user in dayfold_graph.users.items():
                session.run("MERGE (u:User {id: $id, name: $name})", 
                            id=user.user_id, name=user.username)
                
                for followed in user.following:
                    session.run("""
                        MATCH (a:User {id: $aid}), (b:User {id: $bid})
                        MERGE (a)-[:FOLLOWS]->(b)
                    """, aid=user.user_id, bid=followed.user_id)