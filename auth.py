import sqlite3, os, bcrypt
DB_PATH = os.getenv('AUTH_DB_PATH', os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3'))
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_conn(); cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''); conn.commit(); conn.close()
def create_user(username: str, password: str, full_name: str, email: str, phone: str, is_admin: bool = False):
    init_db(); pw_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode('utf-8')
    conn = get_conn(); cur = conn.cursor()
    cur.execute('INSERT INTO users (username, full_name, email, phone, password_hash, is_admin) VALUES (?, ?, ?, ?, ?, ?)',
                (username, full_name, email, phone, hashed, 1 if is_admin else 0))
    conn.commit(); conn.close(); return True
def verify_user(username: str, password: str):
    init_db(); conn = get_conn(); cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,)); row = cur.fetchone(); conn.close()
    if not row: return None
    pw_bytes = password.encode('utf-8')
    if bcrypt.checkpw(pw_bytes, row['password_hash'].encode('utf-8')): return dict(row)
    return None
