"""One-time CLI: APP_JWT_SECRET=... python bootstrap_admin.py <username>"""
import getpass
import sys
import uuid
from sqlalchemy import text
from auth import hash_password, secret_key
from database import engine

if __name__ == '__main__':
    secret_key()
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python bootstrap_admin.py <username>')
    username = sys.argv[1].strip().lower()
    password = getpass.getpass('Admin password (12+ characters): ')
    with engine.begin() as conn:
        if conn.execute(text("SELECT 1 FROM public.app_user WHERE role='admin'")).first():
            raise SystemExit('An administrator already exists; refusing to create another')
        conn.execute(text("INSERT INTO public.app_user(user_id,username,password_hash,role) VALUES (:id,:username,:hash,'admin')"), {'id': str(uuid.uuid4()), 'username': username, 'hash': hash_password(password)})
    print('Administrator created')
