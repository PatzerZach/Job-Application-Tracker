# Instead of doing the following standard implementation of the Object Class
# class User:
#     def __init__(self, user_id, name, username, email, password_hash):
#         self.user_id = user_id
#         self.name = name
#         self.username = username
#         self.email = email
#         self.password_hash = password_hash



# We can use the dataclass decorator from the dataclasses module to automatically
# create the __init__, __repr__, and __eq__ methods. For reference, __init__ is
# the constructor. __repr__ is for debugging, it will actually print a readable
# string of the object. Lastly __eq__ is for comparisons, you can compare two
# User objects to see if they are the equal (have the same data) or not

from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    name: str
    username: str
    email: str
    password_hash: str