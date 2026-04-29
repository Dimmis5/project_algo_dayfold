import random
from models import DayfoldGraph, MyQueue, MyStack


def build_feed(graph: DayfoldGraph, user_id: int, daily_limit: int = 10) -> list:

    if user_id not in graph.users:
        return []

    user = graph.users[user_id]

    # 50%
    followed_queue = MyQueue()
    for followed_user in user.following:
        for board in followed_user.boards:
            for pin in board.pins:
                followed_queue.enqueue(pin)

    followed_pins = []
    while not followed_queue.is_empty():
        followed_pins.append(followed_queue.dequeue())

    # 30% 
    user_categories = {board.category for board in user.boards}
    discovery_stack = MyStack()

    for uid, other_user in graph.users.items():
        if uid == user_id:
            continue
        if other_user in user.following:
            continue
        for board in other_user.boards:
            if board.category in user_categories:
                for pin in board.pins:
                    discovery_stack.push(pin)

    discovery_pins = []
    while not discovery_stack.is_empty():
        discovery_pins.append(discovery_stack.pop())

    # 20% 
    all_pins = []
    for uid, other_user in graph.users.items():
        if uid == user_id:
            continue
        for board in other_user.boards:
            for pin in board.pins:
                all_pins.append(pin)

    random_pins = random.sample(all_pins, min(len(all_pins), max(1, len(all_pins) // 5)))

    # assembly
    n_followed  = int(daily_limit * 0.5)
    n_discovery = int(daily_limit * 0.3)
    n_random    = daily_limit - n_followed - n_discovery

    seen_ids = set()
    feed = []

    for pin in followed_pins[:n_followed] + discovery_pins[:n_discovery] + random_pins[:n_random]:
        if pin.pin_id not in seen_ids:
            seen_ids.add(pin.pin_id)
            feed.append(pin)

    random.shuffle(feed)
    return feed


def anti_scroll_gate(feed: list, pins_seen: int, daily_limit: int = 10) -> dict:

    remaining = daily_limit - pins_seen

    if remaining <= 0:
        return {
            "locked": True,
            "message": "You've reached your daily limit. Share a pin to unlock more!",
            "pins": []
        }

    return {
        "locked": False,
        "message": f"{remaining} pins remaining today.",
        "pins": feed[:remaining]
    }