import sqlite3
from contextlib import closing

def init_db():
    with closing(sqlite3.connect('hyperlinks.db')) as conn, conn, closing(conn.cursor()) as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hyperlinks (
                id INTEGER PRIMARY KEY,
                sheet_name TEXT,
                cell TEXT,
                hyperlink TEXT,
                text_value TEXT,
                definition_cell TEXT,
                used BOOLEAN DEFAULT 0,
                UNIQUE(sheet_name, cell)
            )
        ''')
        conn.commit()

init_db()
