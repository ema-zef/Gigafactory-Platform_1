"""Replaces the four unscoped CRUD routers. Keep their old route names for React."""
from fastapi import APIRouter, Depends
from auth import User, current_user
from access import TABLES, create, delete, options, schema, selectable_options, update, visible_rows

router = APIRouter(tags=['data'], dependencies=[Depends(current_user)])

def register(table):
    # Register separate closures so FastAPI does not interpret a table parameter.
    def list_records(user: User = Depends(current_user)):
        return visible_rows(table, user)
    def add_record(record: dict, user: User = Depends(current_user)):
        return create(table, record, user)
    def edit_record(record_id: int, record: dict, user: User = Depends(current_user)):
        return update(table, record_id, record, user)
    def remove_record(record_id: int, user: User = Depends(current_user)):
        return delete(table, record_id, user)
    def check():
        return schema(table)
    def get_options(user: User = Depends(current_user)):
        return options(table, user)
    def get_selectable(user: User = Depends(current_user)):
        return selectable_options(table, user)
    router.add_api_route('/'+table, list_records, methods=['GET'], name=f'{table}_list')
    router.add_api_route('/'+table, add_record, methods=['POST'], name=f'{table}_create', status_code=201)
    router.add_api_route('/'+table+'/check', check, methods=['GET'], name=f'{table}_check')
    router.add_api_route('/'+table+'/schema', check, methods=['GET'], name=f'{table}_schema')
    if TABLES[table][1]:
        router.add_api_route('/'+table+'/options', get_options, methods=['GET'], name=f'{table}_options')
        router.add_api_route('/'+table+'/selectable', get_selectable, methods=['GET'], name=f'{table}_selectable')
    router.add_api_route('/'+table+'/{record_id}', edit_record, methods=['PUT'], name=f'{table}_update')
    router.add_api_route('/'+table+'/{record_id}', remove_record, methods=['DELETE'], name=f'{table}_delete')

for _table in TABLES:
    register(_table)
