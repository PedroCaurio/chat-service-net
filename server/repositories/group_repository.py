'''
Camada de Abstração para facilitar o desenvolvimento. Sendo responsável apenas
por se comunicar com os dados dos grupos no TinyDB.
'''

from tinydb import Query
from server.models.group import Group
from server.database.database_instance import db, locked_db


def id_query(group_id: str): return Query().group_id == group_id

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
    def get_group_by_id(group_id: str) -> Group | None:   # READ
        with locked_db():
            result = GroupRepository._group_db().get(id_query(group_id))
        if result:
            return Group.from_dict(result)
        return None

    @staticmethod
    def update_group_name(group: Group) -> bool:   # UPDATE
        with locked_db():
            group_db = GroupRepository._group_db()
            if not group_db.contains(id_query(group.group_id)):
                return False
            group_db.update(group.to_dict(), cond=id_query(group.group_id))
        return True

    @staticmethod
    def delete_group_by_id(group_id: str) -> None:   # DELETE
        with locked_db():
            GroupRepository._group_db().remove(cond = id_query(group_id))

    # Utils

    @staticmethod
    def get_all_groups() -> list[Group]:
        with locked_db():
            results = GroupRepository._group_db().all()
        return [Group.from_dict(data) for data in results]

    @staticmethod
    def get_group_members(group_id: str) -> list[str] | None:
        with locked_db():
            result = GroupRepository._group_db().get(cond = id_query(group_id))
        if result:
            group = Group.from_dict(result)
            return group.users
        return None

    @staticmethod
    def delete_group_by_id(group_id: str) -> None:
        GroupRepository._group_db().remove(cond = id_query(group_id))
    
    @staticmethod
    def get_user_groups(user_id: str) -> list[Group]:
        with locked_db():
            results = GroupRepository._group_db().search(Query().users.any([user_id]))
        return [Group.from_dict(data) for data in results]

    # User Utils

    @staticmethod
    def add_user_to_group(group_id: str, user_id: str) -> bool:
        with locked_db():
            group_db = GroupRepository._group_db()
            group = group_db.get(id_query(group_id))
            if group:
                group_data = Group.from_dict(group)
                if user_id not in group_data.users:
                    group_data.users.append(user_id)
                    group_db.update(group_data.to_dict(), cond=id_query(group_id))
                    return True
        return False

    @staticmethod
    def remove_user_from_group(group_id: str, user_id: str) -> bool:
        with locked_db():
            group_db = GroupRepository._group_db()
            group = group_db.get(id_query(group_id))
            if group:
                group_data = Group.from_dict(group)
                if user_id in group_data.users:
                    group_data.users.remove(user_id)
                    group_db.update(group_data.to_dict(), cond=id_query(group_id))
                    return True
        return False