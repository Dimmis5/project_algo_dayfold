import networkx as nx

from models import DayfoldGraph


def build_interaction_weights(graph: DayfoldGraph) -> nx.Graph:
    interaction_graph = nx.Graph()

    for user_id, user in graph.users.items():
        interaction_graph.add_node(
            user_id,
            username=user.username,
            name=user.name,
            email=user.email,
        )

    def add_weight(u1, u2, weight):
        if u1 == u2:
            return
        if interaction_graph.has_edge(u1, u2):
            interaction_graph[u1][u2]["weight"] += weight
        else:
            interaction_graph.add_edge(u1, u2, weight=weight)

    for user_id, user in graph.users.items():
        for followed in user.following:
            add_weight(user_id, followed.user_id, 5)

        for pin_id in getattr(user, "liked_pins", set()):
            pin = graph.find_pin(pin_id)
            if pin:
                for other_user_id in pin.liked_by:
                    add_weight(user_id, other_user_id, 2)

        for pin_id in getattr(user, "saved_pins", set()):
            pin = graph.find_pin(pin_id)
            if pin:
                for other_user_id in pin.saved_by:
                    add_weight(user_id, other_user_id, 3)

        for pin_id in getattr(user, "shared_pins", set()):
            pin = graph.find_pin(pin_id)
            if pin:
                for other_user_id in pin.shared_by:
                    add_weight(user_id, other_user_id, 4)

    return interaction_graph


def _compute_modularity(communities: dict, weights: dict, total_weight: float) -> float:

    degree = {}
    for (u1, u2), w in weights.items():
        degree[u1] = degree.get(u1, 0) + w
        degree[u2] = degree.get(u2, 0) + w

    node_to_comm = {}
    for comm_id, members in communities.items():
        for node in members:
            node_to_comm[node] = comm_id

    Q = 0.0
    for (u1, u2), w in weights.items():
        if node_to_comm.get(u1) == node_to_comm.get(u2):
            ki = degree.get(u1, 0)
            kj = degree.get(u2, 0)
            Q += w - (ki * kj) / (2 * total_weight)

    return Q / (2 * total_weight) if total_weight > 0 else 0.0


def louvain(graph: DayfoldGraph) -> dict:

    interaction_graph = build_interaction_weights(graph)
    total_weight = interaction_graph.size(weight="weight")
    
    if total_weight == 0:
        return {uid: uid for uid in graph.users}

    partition = {uid: uid for uid in graph.users}

    neighbors = {uid: set() for uid in graph.users}
    for u1, u2 in interaction_graph.edges():
        neighbors[u1].add(u2)
        neighbors[u2].add(u1)

    improved = True
    while improved:
        improved = False

        for user_id in graph.users:
            current_comm = partition[user_id]

            comm_weights = {}
            for neigh in neighbors.get(user_id, set()):
                neigh_comm = partition[neigh]
                w = interaction_graph[user_id][neigh].get("weight", 1)
                comm_weights[neigh_comm] = comm_weights.get(neigh_comm, 0) + w

            if not comm_weights:
                continue

            best_comm = max(comm_weights, key=lambda c: comm_weights[c])

            if best_comm != current_comm and comm_weights[best_comm] > comm_weights.get(current_comm, 0):
                partition[user_id] = best_comm
                improved = True

    unique_comms = {c: i for i, c in enumerate(set(partition.values()))}
    return {uid: unique_comms[comm] for uid, comm in partition.items()}
