import sqlite3
import json
import os
from config.settings import DB_PATH

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    """
    Initializes local database directory and connection.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    conn.close()
    print("Database initialized successfully.")
