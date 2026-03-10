import sqlite3
import os
import contextlib
import urllib.parse
import re

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "database.db")
DATABASE_URL = os.environ.get("DATABASE_URL")

class PgCursorWrapper:
    """Wrapper to make psycopg2 cursor behave like sqlite3 cursor for existing queries."""
    def __init__(self, cursor):
        self.cursor = cursor
        
    def execute(self, query, params=None):
        # Replace SQLite '?' placeholder with PostgreSQL '%s' placeholder
        # Simple string replacement since our queries don't contain '?' inside quotes.
        query = query.replace("?", "%s")
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
            
    def fetchone(self):
        row = self.cursor.fetchone()
        return dict(row) if row else None
        
    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
        
    def __getattr__(self, name):
        return getattr(self.cursor, name)

class PgConnectionWrapper:
    """Wrapper to make psycopg2 connection return our wrapped cursor."""
    def __init__(self, conn):
        self.conn = conn
        
    def cursor(self):
        return PgCursorWrapper(self.conn.cursor())
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()

def get_db_connection():
    """
    Returns a database connection with dictionary-like row access enabled.
    Supports either PostgreSQL (if DATABASE_URL is set) or SQLite fallback.
    """
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Parse connection string
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(DATABASE_URL)
        
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            cursor_factory=RealDictCursor
        )
        return PgConnectionWrapper(conn)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

@contextlib.contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
