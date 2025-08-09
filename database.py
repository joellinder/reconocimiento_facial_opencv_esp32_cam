# database.py
import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_FILE = "database.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    first_time = not os.path.exists(DB_FILE)
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS autorizados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        filename TEXT NOT NULL,
        embedding_hex TEXT
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS intrusos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        fecha_hora TEXT NOT NULL,
        embedding_hex TEXT
    )''')

    conn.commit()

    if first_time:
        # crear admin por defecto
        pwd_hash = generate_password_hash("1234")
        c.execute("INSERT INTO usuarios (username, password, is_admin) VALUES (?, ?, ?)",
                  ("admin", pwd_hash, 1))
        conn.commit()
        print("[INIT] Usuario admin creado: admin / 1234")

    conn.close()

# ---- Usuarios ----
def add_user(username, password_hash, is_admin=0):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (username, password, is_admin, password) VALUES (?, ?, ?, ?)",
              (username, is_admin, is_admin, password_hash))  # legacy insertion (harmless)
    # proper insertion
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (username, password, is_admin) VALUES (?, ?, ?)",
              (username, password_hash, is_admin))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_by_id(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    return row

def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM usuarios ORDER BY id").fetchall()
    conn.close()
    return rows

def update_user(uid, new_username=None, new_password_hash=None, is_admin=None):
    conn = get_connection()
    c = conn.cursor()
    if new_username is not None:
        c.execute("UPDATE usuarios SET username = ? WHERE id = ?", (new_username, uid))
    if new_password_hash is not None:
        c.execute("UPDATE usuarios SET password = ? WHERE id = ?", (new_password_hash, uid))
    if is_admin is not None:
        c.execute("UPDATE usuarios SET is_admin = ? WHERE id = ?", (is_admin, uid))
    conn.commit()
    conn.close()

def delete_user(uid):
    conn = get_connection()
    conn.execute("DELETE FROM usuarios WHERE id = ?", (uid,))
    conn.commit()
    conn.close()

# ---- Autorizados ----
def add_autorizado(nombre, filename, embedding_hex=None):
    conn = get_connection()
    conn.execute("INSERT INTO autorizados (nombre, filename, embedding_hex) VALUES (?, ?, ?)",
                 (nombre, filename, embedding_hex))
    conn.commit()
    conn.close()

def list_autorizados():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM autorizados ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def get_autorizado(aid):
    conn = get_connection()
    row = conn.execute("SELECT * FROM autorizados WHERE id = ?", (aid,)).fetchone()
    conn.close()
    return row

def delete_autorizado(aid):
    conn = get_connection()
    row = conn.execute("SELECT filename FROM autorizados WHERE id = ?", (aid,)).fetchone()
    if row:
        filename = row["filename"]
        path = os.path.join("data", "autorizados", filename)
        try:
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
    conn = get_connection()
    conn.execute("DELETE FROM autorizados WHERE id = ?", (aid,))
    conn.commit()
    conn.close()

def update_autorizado_embedding(aid, embedding_hex):
    conn = get_connection()
    conn.execute("UPDATE autorizados SET embedding_hex = ? WHERE id = ?", (embedding_hex, aid))
    conn.commit()
    conn.close()

# ---- Intrusos ----
def add_intruso(filename, fecha_hora, embedding_hex=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO intrusos (filename, fecha_hora, embedding_hex) VALUES (?, ?, ?)",
                (filename, fecha_hora, embedding_hex))
    conn.commit()
    lastid = cur.lastrowid
    conn.close()
    return lastid

def list_intrusos():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM intrusos ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def get_last_intruso():
    conn = get_connection()
    row = conn.execute("SELECT * FROM intrusos ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return row

def delete_intruso(iid):
    conn = get_connection()
    row = conn.execute("SELECT filename FROM intrusos WHERE id = ?", (iid,)).fetchone()
    if row:
        filename = row["filename"]
        path = os.path.join("data", "intrusos", filename)
        try:
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
    conn = get_connection()
    conn.execute("DELETE FROM intrusos WHERE id = ?", (iid,))
    conn.commit()
    conn.close()