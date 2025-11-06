from backend.services import *

create_user("alice", "password123")
print(get_all_users())