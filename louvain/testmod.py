import networkx as nx
from networkx.algorithms.community.quality import modularity

# =========================
# 1. CRÉATION DU GRAPHE
# =========================

G = nx.Graph()

# Petites paires fortes
G.add_edge("A", "B", weight=30)
G.add_edge("C", "D", weight=30)
G.add_edge("E", "F", weight=30)
G.add_edge("G", "H", weight=30)

# Liens entre paires du même grand bloc
G.add_edge("A", "C", weight=10)
G.add_edge("A", "D", weight=10)
G.add_edge("B", "C", weight=10)
G.add_edge("B", "D", weight=10)

G.add_edge("E", "G", weight=10)
G.add_edge("E", "H", weight=10)
G.add_edge("F", "G", weight=10)
G.add_edge("F", "H", weight=10)

# Liens faibles entre grands blocs
G.add_edge("B", "E", weight=1)
G.add_edge("D", "G", weight=1)
G.add_edge("C", "F", weight=1)


# =========================
# 2. FONCTION DE TEST
# =========================

def test_modularity(graph, partition_dict, name):
    """
    partition_dict = dictionnaire du type :
    {
        "c0": ["A", "B"],
        "c1": ["C", "D"]
    }
    """

    communities = [
        nodes
        for nodes in partition_dict.values()
        if len(nodes) > 0
    ]

    q = modularity(graph, communities, weight="weight")

    print("\n==============================")
    print(name)
    print("==============================")
    print("Communautés :")
    for comm, nodes in partition_dict.items():
        if len(nodes) > 0:
            print(comm, "=", nodes)

    print("Modularité =", q)
    return q


# =========================
# 3. TEST DES PARTITIONS
# =========================

# Niveau 0 : chaque nœud seul
partition_0 = {
    "A": ["A"],
    "B": ["B"],
    "C": ["C"],
    "D": ["D"],
    "E": ["E"],
    "F": ["F"],
    "G": ["G"],
    "H": ["H"],
}

# Niveau 1 : petites paires
partition_1 = {
    "c0": ["A", "B"],
    "c1": ["C", "D"],
    "c2": ["E", "F"],
    "c3": ["G", "H"],
}

# Niveau 2 : deux grands blocs
partition_2 = {
    "C0": ["A", "B", "C", "D"],
    "C1": ["E", "F", "G", "H"],
}

# Niveau 3 : tout fusionné
partition_all = {
    "ALL": ["A", "B", "C", "D", "E", "F", "G", "H"]
}


q0 = test_modularity(G, partition_0, "Niveau 0 : chaque nœud seul")
q1 = test_modularity(G, partition_1, "Niveau 1 : petites paires")
q2 = test_modularity(G, partition_2, "Niveau 2 : grands blocs")
q_all = test_modularity(G, partition_all, "Niveau 3 : tout fusionné")


# =========================
# 4. RÉSUMÉ
# =========================

print("\n==============================")
print("RÉSUMÉ")
print("==============================")
print("Niveau 0 :", q0)
print("Niveau 1 :", q1)
print("Niveau 2 :", q2)
print("Tout fusionné :", q_all)

best = max(
    [
        ("Niveau 0", q0),
        ("Niveau 1", q1),
        ("Niveau 2", q2),
        ("Tout fusionné", q_all),
    ],
    key=lambda x: x[1]
)

print("\nMeilleure partition :", best[0])
print("Meilleure modularité :", best[1])