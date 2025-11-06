from tinydb import Query
from backend.models import Group
from backend.database import db
import uuid

group_db = db.table("groups")

class GroupRepository:
    
    @staticmethod
    def add_group(group: Group) -> None:
        if (group.users is None) or (len(group.users) == 0):
            group.users = [group.admin]
        group_db.insert(group.to_dict())
    
    @staticmethod
    def get_group_by_id(group_id: str) -> Group | None:
        result = group_db.get(Query().group_id == group_id)
        if result:
            return Group.from_dict(result)
        return None
    
    @staticmethod
    def get_all_groups() -> list[Group]:
        results = group_db.all()
        return [Group.from_dict(data) for data in results]
    
    @staticmethod
    def get_group_members(group_id: str) -> list[str] | None:
        result = group_db.get(doc_id=group_id)
        if result:
            group = Group.from_dict(result)
            return group.users
        return None

    @staticmethod
    def delete_group_by_id(group_id: str) -> None:
        group_db.remove(doc_id = group_id)
    
    @staticmethod
    def get_user_groups(user_id: str) -> list[Group]:
        results = group_db.search(Query().users.any([user_id]))
        return [Group.from_dict(data) for data in results]