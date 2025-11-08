from dataclasses import dataclass

@dataclass
class User:
    username: str
    password: str
    user_id: str

    @staticmethod
    def from_dict(data: dict) -> 'User':
        return User(
            user_id=data['user_id'],
            username=data['username'],
            password=data['password']
        )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password": self.password
        }