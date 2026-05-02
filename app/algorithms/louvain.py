from models import DayfoldGraph


def build_interaction_weights(graph: DayfoldGraph) -> dict:
    weights = {}

    for user_id, user in graph.users.items():
        for followed in user.following:
            u1 = min(user_id, followed.user_id)
            u2 = max(user_id, followed.user_id)
            key = (u1, u2)
            weights[key] = weights.get(key, 0) + 5

    return weights


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

    weights = build_interaction_weights(graph)
    total_weight = sum(weights.values())

    if total_weight == 0:
        return {uid: uid for uid in graph.users}

    partition = {uid: uid for uid in graph.users}

    neighbors = {uid: set() for uid in graph.users}
    for (u1, u2) in weights:
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
                key = (min(user_id, neigh), max(user_id, neigh))
                w = weights.get(key, 0)
                comm_weights[neigh_comm] = comm_weights.get(neigh_comm, 0) + w

            if not comm_weights:
                continue

            best_comm = max(comm_weights, key=lambda c: comm_weights[c])

            if best_comm != current_comm and comm_weights[best_comm] > comm_weights.get(current_comm, 0):
                partition[user_id] = best_comm
                improved = True

    unique_comms = {c: i for i, c in enumerate(set(partition.values()))}
    return {uid: unique_comms[comm] for uid, comm in partition.items()}