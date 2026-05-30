class Pin:
    def __init__(
        self,
        pin_id,
        title,
        likes=0,
        description="",
        image_url="",
        category=None,
        creator_id=None,
    ):
        self.pin_id = pin_id
        self.id = pin_id
        self.title = title
        self.name = title
        self.description = description
        self.image_url = image_url
        self.category = category
        self.creator_id = creator_id
        self.likes = likes
        self.liked_by = set()
        self.saved_by = set()
        self.shared_by = set()


class Board:
    def __init__(self, board_id, title, category_node, user_id=None):
        self.board_id = board_id
        self.id = board_id
        self.title = title
        self.name = title
        self.category = category_node
        self.user_id = user_id
        self.pins = []


class User:
    def __init__(self, user_id, username, email=None, password_hash=None):
        self.user_id = user_id
        self.id = user_id
        self.username = username
        self.name = username
        self.email = email
        self.password_hash = password_hash
        self.following = []
        self.boards = []
        self.liked_pins = set()
        self.saved_pins = set()
        self.shared_pins = set()


class DayfoldGraph:
    def __init__(self):
        self.users = {}

    def add_user(self, user_id, username, email=None, password_hash=None):
        if user_id not in self.users:
            self.users[user_id] = User(user_id, username, email, password_hash)
        return self.users[user_id]

    def add_friendship(self, u_id, v_id):
        if u_id in self.users and v_id in self.users:
            if self.users[v_id] not in self.users[u_id].following:
                self.users[u_id].following.append(self.users[v_id])

    def add_board_to_user(self, user_id, board_id, title, category="General"):
        if user_id in self.users:
            new_board = Board(board_id, title, category, user_id=user_id)
            self.users[user_id].boards.append(new_board)
            return new_board
        return None

    def add_pin_to_board(self, board, pin_id, title, likes=0, description="", image_url="", category=None):
        pin_category = category if category is not None else board.category
        new_pin = Pin(
            pin_id,
            title,
            likes,
            description=description,
            image_url=image_url,
            category=pin_category,
            creator_id=board.user_id,
        )
        board.pins.append(new_pin)
        return new_pin

    def find_pin(self, pin_id):
        for user in self.users.values():
            for board in user.boards:
                for pin in board.pins:
                    if pin.pin_id == pin_id:
                        return pin
        return None

    def like_pin(self, user_id, pin_id):
        pin = self.find_pin(pin_id)
        if user_id in self.users and pin:
            self.users[user_id].liked_pins.add(pin_id)
            pin.liked_by.add(user_id)
            pin.likes = len(pin.liked_by)
            return True
        return False

    def save_pin(self, user_id, pin_id):
        pin = self.find_pin(pin_id)
        if user_id in self.users and pin:
            self.users[user_id].saved_pins.add(pin_id)
            pin.saved_by.add(user_id)
            return True
        return False

    def share_pin(self, user_id, pin_id):
        pin = self.find_pin(pin_id)
        if user_id in self.users and pin:
            self.users[user_id].shared_pins.add(pin_id)
            pin.shared_by.add(user_id)
            return True
        return False


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


class MyStack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


class CategoryNode:
    def __init__(self, cat_id, name):
        self.cat_id = cat_id
        self.id = cat_id
        self.name = name
        self.children = []
        self.parent = None

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)
