from models import DayfoldGraph


class MyQueue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def is_empty(self):
        return len(self.items) == 0


def suggest_friends(graph: DayfoldGraph, start_user_id: int) -> list:
    if start_user_id not in graph.users:
        return []

    start_node = graph.users[start_user_id]
    visited = {start_user_id}
    queue = MyQueue()
    queue.enqueue((start_node, 0))
    suggestions = set()

    while not queue.is_empty():
        current_user, dist = queue.dequeue()
        if dist == 2:
            suggestions.add(current_user.username)
        if dist < 2:
            for followed in current_user.following:
                if followed.user_id not in visited:
                    visited.add(followed.user_id)
                    queue.enqueue((followed, dist + 1))

    return list(suggestions)