"""Tests for database schema creation."""

import sqlite3


def test_create_all_tables(temp_db):
    """All expected tables should exist after init_database."""
    con = sqlite3.connect(temp_db)
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cur.fetchall()]
        expected = ["card", "deck", "decklist", "match", "player", "round", "standings"]
        for t in expected:
            assert t in tables, f"Table '{t}' not found"
    finally:
        con.close()


def test_match_table_has_table_number_and_feature(temp_db):
    """match table should have table_number and is_feature_match columns."""
    con = sqlite3.connect(temp_db)
    try:
        cur = con.cursor()
        cur.execute("PRAGMA table_info(match)")
        columns = [row[1] for row in cur.fetchall()]
        assert "table_number" in columns
        assert "is_feature_match" in columns
    finally:
        con.close()


def test_standings_table_exists(temp_db):
    """standings table should exist with correct columns."""
    con = sqlite3.connect(temp_db)
    try:
        cur = con.cursor()
        cur.execute("PRAGMA table_info(standings)")
        columns = [row[1] for row in cur.fetchall()]
        expected = ["id_player", "id_round", "match_record", "game_record", "points"]
        for c in expected:
            assert c in columns, f"Column '{c}' not found in standings"
    finally:
        con.close()
