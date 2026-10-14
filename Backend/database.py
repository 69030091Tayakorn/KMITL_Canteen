import sqlite3
from pathlib import Path


project_folder = Path(__file__).resolve().parent.parent
database_file = project_folder / "Database SQLite" / "canteen.db"


def connect_database():
    # Open an existing database. Create tables manually in DB Browser.
    database_url = database_file.resolve().as_uri() + "?mode=rw"
    connection = sqlite3.connect(database_url, uri=True)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
