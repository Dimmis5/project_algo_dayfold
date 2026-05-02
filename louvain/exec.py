import creation as cr
import importG as Graph
from community import community_louvain


# --------------------
if __name__ == "__main__":
    partition = community_louvain.best_partition(Graph.G,weight="weight")

    print("===== ARÊTES =====")
    for u, v, data in Graph.G.edges(data=True):
        print(u, "--", v, "poids =", data.get("weight", 1))

    for user_id, community_id in partition.items():
        print(f"User {user_id} -> Communauté {community_id}")
        
    with Graph.driver.session() as session:
        for user_id, community_id in partition.items():
            session.run("""
                MATCH (u:User {id: $id})
                SET u.community = $community    
            """, id=user_id, community=community_id)
    """
    # Groupe 1 : fashion / streetwear
    alice_id = cr.create_user("alice", "alice@mail.com", "hash123")
    bob_id = cr.create_user("bob", "bob@mail.com", "hash456")
    charlie_id = cr.create_user("charlie", "charlie@mail.com", "hash789")

    # Groupe 2 : design / luxury
    emma_id = cr.create_user("emma", "emma@mail.com", "hash111")
    david_id = cr.create_user("david", "david@mail.com", "hash222")
    sophia_id = cr.create_user("sophia", "sophia@mail.com", "hash333")

    # Pins groupe 1
    pin1_id = cr.create_pin(
        "Streetwear Outfit",
        "Black hoodie and sneakers inspiration",
        "https://example.com/streetwear.jpg",
        alice_id
    )

    pin2_id = cr.create_pin(
        "Urban Fashion",
        "Oversized jacket and cargo pants",
        "https://example.com/urban.jpg",
        bob_id
    )

    # Pins groupe 2
    pin3_id = cr.create_pin(
        "Luxury Dress",
        "Elegant evening dress inspiration",
        "https://example.com/luxury.jpg",
        emma_id
    )

    pin4_id = cr.create_pin(
        "Minimalist Design",
        "Clean fashion design inspiration",
        "https://example.com/minimal.jpg",
        david_id
    )
    

    # Boards
    board1_id = cr.create_board("Streetwear Ideas", alice_id)
    board2_id = cr.create_board("Luxury Inspiration", emma_id)

    cr.add_pin_to_board(board1_id, pin1_id)
    cr.add_pin_to_board(board1_id, pin2_id)

    cr.add_pin_to_board(board2_id, pin3_id)
    cr.add_pin_to_board(board2_id, pin4_id)

    # Relations fortes dans groupe 1
    cr.follow_user(alice_id, bob_id)
    cr.follow_user(bob_id, charlie_id)
    cr.follow_user(charlie_id, alice_id)

    cr.like_pin(alice_id, pin1_id)
    cr.like_pin(bob_id, pin1_id)
    cr.like_pin(charlie_id, pin1_id)

    cr.save_pin(bob_id, pin2_id)
    cr.share(charlie_id, pin2_id)

    # Relations fortes dans groupe 2
    cr.follow_user(emma_id, david_id)
    cr.follow_user(david_id, sophia_id)
    cr.follow_user(sophia_id, emma_id)

    cr.like_pin(emma_id, pin3_id)
    cr.like_pin(david_id, pin3_id)
    cr.like_pin(sophia_id, pin3_id)

    cr.save_pin(david_id, pin4_id)
    cr.share(sophia_id, pin4_id)

    # Petite relation entre les deux groupes
    cr.follow_user(bob_id, emma_id)

    print("Données de test créées pour Louvain.")
"""