import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "database" / "eternal_weekend.db"


class Db:
    def __init__(self):
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        return connection

    def drop_tables(self, connection):
        connection.execute("DROP TABLE IF EXISTS match")
        connection.execute("DROP TABLE IF EXISTS player")
        connection.execute("DROP TABLE IF EXISTS round")
        connection.execute("DROP TABLE IF EXISTS decklist")
        connection.execute("DROP TABLE IF EXISTS card")
        connection.execute("DROP TABLE IF EXISTS deck")
        connection.commit()

    def create_tables(self, connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS deck (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS decklist (
                id INTEGER PRIMARY KEY,
                id_deck TEXT NOT NULL,
                id_card INTEGER NOT NULL,
                total INTEGER NOT NULL,
                is_sideboard INTEGER NOT NULL,
                is_maindeck INTEGER NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS match (
                id TEXT PRIMARY KEY,
                id_round INTEGER NOT NULL,
                id_player_1 INTEGER NOT NULL,
                id_player_2 INTEGER NOT NULL,
                player_1_wins INTEGER NOT NULL,
                player_2_wins INTEGER NOT NULL,
                text_result TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS round (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS player (
                id INTEGER PRIMARY KEY,
                team_id INTEGER NOT NULL,
                display_name TEXT NOT NULL,
                username TEXT NOT NULL,
                decklist_id TEXT
            )
            """
        )
        connection.commit()
        return connection

    def init_database(self):
        connection = self.get_connection()
        self.drop_tables(connection)
        self.create_tables(connection)
        connection.close()
