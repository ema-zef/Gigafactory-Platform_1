from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from database import engine
from auth import User, admin_only, check_password, current_user, hash_password, token_for
import uuid

router = APIRouter(tags=['authentication'])

class LoginRequest(BaseModel):
    username: str
    password: str

class NewUser(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=12, max_length=256)

@router.post('/login')
def login(credentials: LoginRequest):
    with engine.connect() as conn:
        row = conn.execute(text('SELECT user_id, username, role, password_hash FROM public.app_user WHERE username = :username AND is_active'), {'username': credentials.username.strip().lower()}).mappings().first()
    if not row or not check_password(credentials.password, row['password_hash']):
        raise HTTPException(401, 'Invalid credentials')
    user = User(str(row['user_id']), row['username'], row['role'])
    return {'token': token_for(user), 'token_type': 'bearer', 'user': {'id': user.id, 'username': user.username, 'role': user.role}}

@router.get('/me')
def me(user: User = Depends(current_user)):
    return {'id': user.id, 'username': user.username, 'role': user.role}

@router.post('/users', status_code=201)
def create_user(payload: NewUser, admin: User = Depends(admin_only)):
    username = payload.username.strip().lower()
    if len(username) < 3:
        raise HTTPException(422, 'Username too short')
    with engine.begin() as conn:
        exists = conn.execute(text('SELECT 1 FROM public.app_user WHERE username=:username'), {'username': username}).first()
        if exists:
            raise HTTPException(409, 'Username already exists')
        uid = str(uuid.uuid4())
        conn.execute(text('INSERT INTO public.app_user (user_id,username,password_hash,role) VALUES (:id,:username,:hash,\'user\')'), {'id': uid, 'username': username, 'hash': hash_password(payload.password)})
    return {'id': uid, 'username': username, 'role': 'user'}
