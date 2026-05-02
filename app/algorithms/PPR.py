from collections import defaultdict
from enum import Enum
import heapq


class NodeType(Enum):
    USER  = "user"
    BOARD = "board"
    PIN   = "pin"


class Graph:
    def __init__(self):
        self.edges: dict[str, dict[str, float]] = defaultdict(dict)
        self.node_types: dict[str, NodeType] = {}

    def add_node(self, node_id: str, node_type: NodeType) -> None:
        self.node_types[node_id] = node_type
        if node_id not in self.edges:
            self.edges[node_id] = {}

    def add_edge(self, src: str, dst: str, weight: float = 1.0) -> None:
        self.edges[src][dst] = weight
        if dst not in self.edges:
            self.edges[dst] = {}

    def user_saves_pin(self, user_id: str, pin_id: str) -> None:
        self.add_edge(user_id, pin_id, weight=1.0)
        self.add_edge(pin_id, user_id, weight=0.8)

    def user_follows_board(self, user_id: str, board_id: str) -> None:
        self.add_edge(user_id, board_id, weight=1.0)
        self.add_edge(board_id, user_id, weight=0.6)

    def user_follows_user(self, follower: str, followee: str) -> None:
        self.add_edge(follower, followee, weight=0.8)

    def board_contains_pin(self, board_id: str, pin_id: str) -> None:
        self.add_edge(board_id, pin_id, weight=0.6)
        self.add_edge(pin_id, board_id, weight=0.4)

    def pin_similar_to_pin(self, pin_a: str, pin_b: str, similarity: float) -> None:
        weight = similarity * 0.3
        self.add_edge(pin_a, pin_b, weight)
        self.add_edge(pin_b, pin_a, weight)

    def normalised_neighbors(self, node_id: str) -> list[tuple[str, float]]:
        neighbors = self.edges.get(node_id, {})
        total = sum(neighbors.values())
        if total == 0:
            return []
        return [(dst, w / total) for dst, w in neighbors.items()]


class PersonalizedPageRank:
    def __init__(self, graph: Graph, alpha: float = 0.15, max_iter: int = 100, convergence: float = 1e-6):
        self.graph       = graph
        self.alpha       = alpha
        self.max_iter    = max_iter
        self.convergence = convergence

    def run(self, source_node: str, teleport_set: dict[str, float] | None = None) -> dict[str, float]:
        if teleport_set is None:
            teleport_dist = {source_node: 1.0}
        else:
            total = sum(teleport_set.values())
            teleport_dist = {k: v / total for k, v in teleport_set.items()}

        scores: dict[str, float] = defaultdict(float)
        scores[source_node] = 1.0

        for _ in range(self.max_iter):
            new_scores: dict[str, float] = defaultdict(float)

            for node, score in scores.items():
                if score == 0:
                    continue
                neighbors = self.graph.normalised_neighbors(node)

                # dangling node: redirect its score to the teleport set
                if not neighbors:
                    for t_node, t_weight in teleport_dist.items():
                        new_scores[t_node] += score * t_weight
                    continue

                for neighbor, norm_weight in neighbors:
                    new_scores[neighbor] += (1 - self.alpha) * score * norm_weight

            for t_node, t_weight in teleport_dist.items():
                new_scores[t_node] += self.alpha * t_weight

            max_delta = max(
                abs(new_scores[n] - scores[n]) for n in set(new_scores) | set(scores)
            )
            scores = new_scores

            if max_delta < self.convergence:
                break

        return dict(scores)


def build_topic_teleport_set(
    graph: Graph,
    user_id: str,
    top_n_boards: int = 5,
    user_weight: float = 0.5,
) -> dict[str, float]:
    boards = [
        (w, dst)
        for dst, w in graph.edges.get(user_id, {}).items()
        if graph.node_types.get(dst) == NodeType.BOARD
    ]
    top_boards = heapq.nlargest(top_n_boards, boards)

    if not top_boards:
        return {user_id: 1.0}

    board_weight = (1.0 - user_weight) / len(top_boards)
    teleport = {user_id: user_weight}
    for _, board_id in top_boards:
        teleport[board_id] = board_weight

    return teleport


class FeedBuilder:
    def __init__(self, graph: Graph, ppr: PersonalizedPageRank):
        self.graph = graph
        self.ppr   = ppr

    def build_feed(
        self,
        user_id: str,
        seen_pins: set[str],
        feed_size: int = 60,
        teleport_set: dict[str, float] | None = None,
    ) -> dict[str, list[str]]:
        scores = self.ppr.run(user_id, teleport_set=teleport_set)

        followed_users = {
            dst for dst, w in self.graph.edges.get(user_id, {}).items()
            if self.graph.node_types.get(dst) == NodeType.USER
        }

        SERENDIPITY_THRESHOLD = 0.001
        followed_pins, discovery_pins, serendipity_pins = [], [], []

        for node_id, score in scores.items():
            if self.graph.node_types.get(node_id) != NodeType.PIN:
                continue
            if node_id in seen_pins:
                continue

            pin_neighbors = self.graph.edges.get(node_id, {})
            saved_by_followed = any(n in followed_users for n in pin_neighbors)

            if saved_by_followed:
                followed_pins.append((score, node_id))
            elif score >= SERENDIPITY_THRESHOLD:
                discovery_pins.append((score, node_id))
            else:
                serendipity_pins.append((score, node_id))

        followed_pins.sort(reverse=True)
        discovery_pins.sort(reverse=True)
        serendipity_pins.sort(reverse=False)  # farthest nodes first

        n_followed    = int(feed_size * 0.50)
        n_discovery   = int(feed_size * 0.30)
        n_serendipity = feed_size - n_followed - n_discovery

        return {
            "followed":    [pid for _, pid in followed_pins[:n_followed]],
            "discovery":   [pid for _, pid in discovery_pins[:n_discovery]],
            "serendipity": [pid for _, pid in serendipity_pins[:n_serendipity]],
        }
    

def build_graph_from_dayfold(dayfold_graph) -> Graph:
    g = Graph()

    for user_id, user in dayfold_graph.users.items():
        uid = str(user_id)
        g.add_node(uid, NodeType.USER)

        for board in user.boards:
            bid = str(board.board_id)
            g.add_node(bid, NodeType.BOARD)
            g.user_follows_board(uid, bid)

            for pin in board.pins:
                pid = str(pin.pin_id)
                g.add_node(pid, NodeType.PIN)
                g.board_contains_pin(bid, pid)
                g.user_saves_pin(uid, pid) 
        for followed in user.following:
            g.user_follows_user(uid, str(followed.user_id))

    return g