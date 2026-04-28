
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

    def add_friendship(self, u_id, v_id):
        if u_id in self.users and v_id in self.users:
            self.users[u_id].following.append(self.users[v_id])