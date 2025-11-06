from dataclasses import dataclass

@dataclass
class Group:
    admin: str
    users: list[str]
    name: str
    created_at: int
    group_id: str | None = None

    @staticmethod
    def from_dict(data: dict) -> 'Group':
        return Group(
            admin=data["admin"],
            users=data["users"],
            group_id=data['group_id'],
            name=data['name'],
            created_at=data['created_at']
        )
    
    def to_dict(self) -> dict:
        return {
            "group_id": self.group_id,
            "admin": self.admin,
            "users": self.users,
            "name": self.name,
            "created_at": self.created_at
        }


