# app/auth.py
import bcrypt

# Usuário provisório (troque depois)
USERS = {
    "leonardo": {
        "full_name": "Leonardo Lopes de Souza",
        "email": "leonardolopesesouza@gmail.com",
        "password_hash": bcrypt.hashpw("Ked0724%@c".encode(), bcrypt.gensalt()).decode()
    }
}

def verify_user(username: str, password: str):
    """Verifica usuário e senha"""
    user = USERS.get(username)
    if not user:
        return None
    try:
        if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return user
    except Exception:
        return None
    return None