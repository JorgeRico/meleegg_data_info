"""Tests for database insert operations."""

import sqlite3


def test_insert_player(temp_db):
    con = sqlite3.connect(temp_db)
    try:
        con.execute(
            "INSERT INTO player (id, team_id, display_name, username, decklist_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (1, 10, "Test Player", "testuser", "deck-1"),
        )
        con.commit()
        cur = con.execute("SELECT display_name FROM player WHERE id = ?", (1,))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "Test Player"
    finally:
        con.close()


def test_insert_match_with_feature_flag(temp_db):
    con = sqlite3.connect(temp_db)
    try:
        con.execute(
            "INSERT INTO player (id, team_id, display_name, username, decklist_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (1, 10, "Alice", "alice", None),
        )
        con.execute(
            "INSERT INTO player (id, team_id, display_name, username, decklist_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (2, 11, "Bob", "bob", None),
        )
        con.execute("INSERT INTO round (id, name) VALUES (?, ?)", (1, "Round 1"))
        con.execute(
            "INSERT INTO match (id, id_round, id_player_1, id_player_2, "
            "player_1_wins, player_2_wins, text_result, table_number, is_feature_match) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("m1", 1, 1, 2, 2, 0, "Alice won", 5, 1),
        )
        con.commit()
        cur = con.execute(
            "SELECT table_number, is_feature_match FROM match WHERE id = ?",
            ("m1",),
        )
        row = cur.fetchone()
        assert row is not None
        assert row[0] == 5
        assert row[1] == 1
    finally:
        con.close()
