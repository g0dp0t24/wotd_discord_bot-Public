import sqlite3
from contextlib import closing
import logging, os

logger = logging.getLogger(__name__)

default_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hyperlinks.db')

def init_db(db_path: str | None = None) -> None:
    if db_path is None:
        db_path = default_db_path

    with closing(sqlite3.connect(db_path)) as conn, conn, closing(conn.cursor()) as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hyperlinks (
                id INTEGER PRIMARY KEY,
                sheet_name TEXT,
                cell TEXT,
                hyperlink TEXT,
                text_value TEXT,
                definition_cell TEXT,
                used BOOLEAN DEFAULT 0,
                processed BOOLEAN DEFAULT 0,
                UNIQUE(sheet_name, cell)
            )
        ''')
        conn.commit()
