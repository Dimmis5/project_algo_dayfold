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

    def sync_graph(self, dayfold_graph, communities: dict = None):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            
            # Users
            for u_id, user in dayfold_graph.users.items():
                community_id = communities[u_id] if communities and u_id in communities else -1
                session.run(
                    """
                    MERGE (u:User {id: $id})
                    SET u.username = $username,
                        u.name = $username,
                        u.email = $email,
                        u.community = $community
                    """,
                    id=str(user.user_id),
                    username=user.username,
                    email=getattr(user, "email", None),
                    community=community_id,
                )

            # Boards et Pins
            for u_id, user in dayfold_graph.users.items():
                for board in user.boards:
                    category_name = board.category.name if hasattr(board.category, 'name') else str(board.category)
                    session.run(
                        """
                        MERGE (b:Board {id: $bid})
                        SET b.title = $title,
                            b.name = $title,
                            b.category = $category,
                            b.user_id = $uid
                        """,
                        bid=str(board.board_id),
                        title=board.title,
                        category=category_name,
                        uid=str(user.user_id),
                    )

                    for pin in board.pins:
                        pin_category = pin.category.name if hasattr(pin.category, 'name') else (
                            str(pin.category) if pin.category is not None else category_name
                        )
                        session.run(
                            """
                            MERGE (p:Pin {id: $pid})
                            SET p.title = $ptitle,
                                p.name = $ptitle,
                                p.description = $description,
                                p.image_url = $image_url,
                                p.category = $category,
                                p.creator_id = $creator_id,
                                p.likes = $likes
                            """,
                            pid=str(pin.pin_id),
                            ptitle=pin.title,
                            description=getattr(pin, "description", ""),
                            image_url=getattr(pin, "image_url", ""),
                            category=pin_category,
                            creator_id=str(getattr(pin, "creator_id", user.user_id)),
                            likes=getattr(pin, "likes", 0),
                        )

            # Relations
            for u_id, user in dayfold_graph.users.items():
                for followed in user.following:
                    session.run("""
                        MATCH (a:User {id: $aid}), (b:User {id: $bid})
                        MERGE (a)-[:FOLLOWS]->(b)
                    """, aid=str(user.user_id), bid=str(followed.user_id))

                for board in user.boards:
                    session.run("""
                        MATCH (u:User {id: $uid}), (b:Board {id: $bid})
                        MERGE (u)-[:CREATED]->(b)
                        MERGE (u)-[:OWNS]->(b)
                    """, uid=str(user.user_id), bid=str(board.board_id))

                    for pin in board.pins:
                        session.run("""
                            MATCH (b:Board {id: $bid}), (p:Pin {id: $pid})
                            MERGE (b)-[:CONTAINS]->(p)
                        """, bid=str(board.board_id), pid=str(pin.pin_id))

                        session.run("""
                            MATCH (u:User {id: $uid}), (p:Pin {id: $pid})
                            MERGE (u)-[:CREATED]->(p)
                        """, uid=str(user.user_id), pid=str(pin.pin_id))

                        for liked_user_id in getattr(pin, "liked_by", set()):
                            session.run("""
                                MATCH (u:User {id: $uid}), (p:Pin {id: $pid})
                                MERGE (u)-[:LIKED]->(p)
                            """, uid=str(liked_user_id), pid=str(pin.pin_id))

                        for saved_user_id in getattr(pin, "saved_by", set()):
                            session.run("""
                                MATCH (u:User {id: $uid}), (p:Pin {id: $pid})
                                MERGE (u)-[:SAVED]->(p)
                            """, uid=str(saved_user_id), pid=str(pin.pin_id))

                        for shared_user_id in getattr(pin, "shared_by", set()):
                            session.run("""
                                MATCH (u:User {id: $uid}), (p:Pin {id: $pid})
                                MERGE (u)-[:SHARED]->(p)
                            """, uid=str(shared_user_id), pid=str(pin.pin_id))
