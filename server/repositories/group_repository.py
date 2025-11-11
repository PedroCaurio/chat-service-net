'''
Camada de Abstração para facilitar o desenvolvimento. Sendo responsável apenas
por se comunicar com os dados dos grupos no TinyDB.
'''

from tinydb import Query
from models.group import Group
from database.database_instance import db, locked_db


def name_query(group_name: str): return Query().group_name == group_name

class GroupRepository:

    @staticmethod
    def _group_db():
        return db.table("groups")

    # CRUD Operations

    @staticmethod
    def add_group(group: Group) -> None:   # CREATE
        if (group.users is None) or (len(group.users) == 0):
            group.users = [group.admin]
        with locked_db():
            GroupRepository._group_db().insert(group.to_dict())

    @staticmethod
    def update_group_name(group: Group) -> bool:   # UPDATE
        with locked_db():
            group_db = GroupRepository._group_db()
            if not group_db.contains(name_query(group.group_name)):
                return False
            group_db.update(group.to_dict(), cond=name_query(group.group_name))
        return True

    @staticmethod
    def delete_group_by_name(group_name: str) -> None:   # DELETE
        with locked_db():
            GroupRepository._group_db().remove(cond = name_query(group_name))

    # Utils

    @staticmethod
    def get_all_groups() -> list[Group]:
        with locked_db():
            results = GroupRepository._group_db().all()
        return [Group.from_dict(data) for data in results]

    @staticmethod
    def get_group_members(group_name: str) -> list[str] | None:
        with locked_db():
            result = GroupRepository._group_db().get(cond = name_query(group_name))
        if result:
            group = Group.from_dict(result)
            return group.users
        return None

    @staticmethod
    def delete_group_by_name(group_name: str) -> None:
        GroupRepository._group_db().remove(cond = name_query(group_name))
    
    @staticmethod
    def get_user_groups(username: str) -> list[Group]:
        with locked_db():
            results = GroupRepository._group_db().search(Query().users.any([username]))
        return [Group.from_dict(data) for data in results]

    # User Utils

    @staticmethod
    def add_user_to_group(group_name: str, username: str) -> bool:
        with locked_db():
            group_db = GroupRepository._group_db()
            group = group_db.get(name_query(group_name))
            if group:
                group_data = Group.from_dict(group)
                if username not in group_data.users:
                    group_data.users.append(username)
                    group_db.update(group_data.to_dict(), cond=name_query(group_name))
                    return True
        return False

    @staticmethod
    def remove_user_from_group(group_name: str, username: str) -> bool:
        with locked_db():
            group_db = GroupRepository._group_db()
            group = group_db.get(name_query(group_name))
            if group:
                group_data = Group.from_dict(group)
                if username in group_data.users:
                    group_data.users.remove(username)
                    group_db.update(group_data.to_dict(), cond=name_query(group_name))
                    return True
        return False