import sqlite3 as sql


def connect_db(path):
    conn = sql.connect(path)
    conn.row_factory = sql.Row
    return conn


def create_db(db_path, db_script_path):
    db = connect_db(db_path)
    with open(db_script_path, mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()
