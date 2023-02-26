from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, user_type):
        self.id = id
        self.email = email
        self.password = password
        self.user_type = user_type
    
    def setId(self, id):
        self.id = id