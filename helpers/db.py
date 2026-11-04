import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database" / "eternal_weekend.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS deck (
            id INTEGER PRIMARY KEY,
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
            id_deck INTEGER NOT NULL,
            id_card INTEGER NOT NULL,
            total INTEGER NOT NULL,
            is_sideboard INTEGER NOT NULL,
            is_maindeck INTEGER NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS standings (
            id INTEGER PRIMARY KEY,
            id_round INTEGER NOT NULL,
            id_player_1 INTEGER NOT NULL,
            id_player_2 INTEGER NOT NULL,
            player_1_wins INTEGER NOT NULL,
            player_2_wins INTEGER NOT NULL,
            text_result TEXT NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def init_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = get_connection()
    create_tables(connection)
    connection.close()
