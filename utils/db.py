import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'artstore.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # users table
    c.execute('''
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
      )
    ''')
    # artworks table
    c.execute('''
      CREATE TABLE IF NOT EXISTS artworks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_id INTEGER,
        title TEXT, price REAL,
        description TEXT,
        filename TEXT,
        FOREIGN KEY(artist_id) REFERENCES users(id)
      )
    ''')
    # carts table
    c.execute('''
      CREATE TABLE IF NOT EXISTS carts (
        user_id INTEGER,
        art_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(art_id) REFERENCES artworks(id)
      )
    ''')
    conn.commit()
    conn.close()

# User functions
def add_user(username, password, role):
    conn = get_conn()
    try:
        conn.execute(
          'INSERT INTO users(username,password,role) VALUES (?,?,?)',
          (username, password, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_conn()
    cur = conn.execute(
      'SELECT id, username, role FROM users WHERE username=? AND password=?',
      (username, password)
    )
    row = cur.fetchone()
    conn.close()
    return row

# Artwork functions
def add_artwork(artist_id, title, description, price, filename):
    conn = get_conn()
    conn.execute(
      'INSERT INTO artworks(artist_id,title,description,price,filename) '
      'VALUES (?,?,?,?,?)',
      (artist_id, title, description, price, filename)
    )
    conn.commit()
    conn.close()

def get_all_artworks():
    conn = get_conn()
    cur = conn.execute('''
      SELECT a.id, u.username AS artist, a.title, a.description,
             a.price, a.filename
      FROM artworks a
      JOIN users u ON a.artist_id=u.id
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows

# Cart functions
def add_to_cart(user_id, art_id):
    conn = get_conn()
    conn.execute(
      'INSERT INTO carts(user_id, art_id) VALUES (?,?)',
      (user_id, art_id)
    )
    conn.commit()
    conn.close()

def get_cart_items(user_id):
    conn = get_conn()
    cur = conn.execute('''
      SELECT art.title, art.description, art.price, art.filename, u.username AS artist
      FROM carts c
      JOIN artworks art ON c.art_id = art.id
      JOIN users u ON art.artist_id = u.id
      WHERE c.user_id = ?
    ''', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def clear_cart(user_id):
    conn = get_conn()
    conn.execute('DELETE FROM carts WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()
