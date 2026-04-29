from neo4j import GraphDatabase
import networkx as nx

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testinglimit"))

G = nx.Graph()


with driver.session() as session:
    session.run("""
        MATCH (:User)-[s:SIMILAR]-(:User)
        DELETE s
    """)
    session.run("""
            MATCH (u1:User)-[r1:LIKED|SAVED|SHARED|FOLLOWS]->(x)<-[r2:LIKED|SAVED|SHARED|FOLLOWS]-(u2:User)
            WHERE u1.id < u2.id
            WITH u1, u2,
                sum(CASE WHEN type(r1) = "LIKED" THEN 1 ELSE 0 END) AS liked,
                sum(CASE WHEN type(r1) = "SAVED" THEN 1 ELSE 0 END) AS saved,
                sum(CASE WHEN type(r1) = "SHARED" THEN 1 ELSE 0 END) AS shared,
                sum(CASE WHEN type(r1) = "FOLLOWS" THEN 1 ELSE 0 END) AS followed
            MERGE (u1)-[s:SIMILAR]-(u2)
            SET s.liked = liked,
                s.saved = saved,
                s.shared = shared,
                s.followed= followed,
                s.weight = liked * 2+ followed * 2 + saved * 3 + shared * 4;
    """)
    session.run("""
            MATCH (u1:User)-[:FOLLOWS]->(u2:User)
            MERGE (u1)-[s:SIMILAR]-(u2)
            SET s.direct_follow = 1,
                s.weight = coalesce(s.weight, 0) + 5
        """)
    result=session.run("""
            MATCH (u1:User)-[s:SIMILAR]->(u2:User)
            RETURN u1.id AS source,u2.id AS target,s.weight AS weight
        """)
        
    for record in result:
        G.add_edge(record["source"], record["target"], weight=record["weight"])