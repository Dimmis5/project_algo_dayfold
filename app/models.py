class Pin:
    def __init__(self, pin_id, title, likes=0):
        self.pin_id = pin_id
        self.title = title
        self.likes = likes

class Board:
    def __init__(self, board_id, title, category):
        self.board_id = board_id
        self.title = title
        self.category = category
        self.pins = []

class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.following = [] 
        self.boards = []    

class DayfoldGraph:
    def __init__(self):
        self.users = {} 

    def add_user(self, user_id, username):
        if user_id not in self.users:
            new_user = User(user_id, username)
            self.users[user_id] = new_user
            return new_user
        return self.users[user_id]

    def add_friendship(self, u_id, v_id):
        if u_id in self.users and v_id in self.users:
            self.users[u_id].following.append(self.users[v_id])


    def add_board_to_user(self, user_id, board_id, title, category="Général"):
        if user_id in self.users:
            new_board = Board(board_id, title, category)
            self.users[user_id].boards.append(new_board)
            return new_board
        return None

    def add_pin_to_board(self, board, pin_id, title, likes=0):
        new_pin = Pin(pin_id, title, likes)
        board.pins.append(new_pin)
        return new_pin
    

# --- STRUCTURES DE DONNÉES (Cours 5, p.43) ---

class MyQueue:
    """Implémentation manuelle d'une File (FIFO)"""
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0) # Retire le premier élément
        return None

    def is_empty(self):
        return len(self.items) == 0

class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.following = [] 
        self.boards = []

class DayfoldGraph:
    def __init__(self):
        self.users = {} 

    def add_user(self, user_id, username):
        if user_id not in self.users:
            new_user = User(user_id, username)
            self.users[user_id] = new_user
            return new_user
        return self.users[user_id]

    def add_friendship(self, u_id, v_id):
        if u_id in self.users and v_id in self.users:
            self.users[u_id].following.append(self.users[v_id])

    def add_board_to_user(self, user_id, board_id, title, category="Général"):
        if user_id in self.users:
            new_board = Board(board_id, title, category)
            self.users[user_id].boards.append(new_board)
            return new_board
        return None

    def add_pin_to_board(self, board, pin_id, title, likes=0):
        new_pin = Pin(pin_id, title, likes)
        board.pins.append(new_pin)
        return new_pin

    def suggest_friends(self, start_user_id):
        if start_user_id not in self.users:
            return []

        start_node = self.users[start_user_id]
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