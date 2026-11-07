"""Tests for Match class."""

from classes.Match import Match
from classes.db import Db


def test_match_creation(sample_match):
    assert sample_match.id == "abc-123-def-456"
    assert sample_match.id_round == 5001
    assert sample_match.id_player_1 == 4001
    assert sample_match.id_player_2 == 4002
    assert sample_match.player_1_wins == 2
    assert sample_match.player_2_wins == 0
    assert sample_match.text_result == "Alice Player won 2-0-0"
    assert sample_match.table_number == 4
    assert sample_match.is_feature_match == 0


def test_match_from_match_data(sample_match_data):
    matches = Match.from_match_data(sample_match_data)
    assert len(matches) == 1

    m = matches[0]
    assert m.id == "abc-123-def-456"
    assert m.id_round == 5001
    assert m.id_player_1 == 4001  # Alice
    assert m.id_player_2 == 4002  # Bob
    assert m.player_1_wins == 2
    assert m.player_2_wins == 0
    assert m.text_result == "Alice Player won 2-0-0"
    assert m.table_number == 4
    assert m.is_feature_match == 0


def test_match_from_match_data_empty():
    matches = Match.from_match_data([])
    assert matches == []


def test_match_insert_all(temp_db):
    db = Db()
    connection = db.get_connection()
    try:
        # Insert players first (foreign key)
        connection.execute(
            "INSERT INTO player (id, team_id, display_name, username, decklist_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (4001, 7001, "Alice", "alice", None),
        )
        connection.execute(
            "INSERT INTO player (id, team_id, display_name, username, decklist_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (4002, 7002, "Bob", "bob", None),
        )
        connection.commit()

        m = Match(
            id="m-1", id_round=5001, id_player_1=4001, id_player_2=4002,
            player_1_wins=2, player_2_wins=0, text_result="2-0-0",
            table_number=1, is_feature_match=1,
        )
        Match.insert_all(connection, [m])
        connection.commit()

        cursor = connection.execute(
            "SELECT id, table_number, is_feature_match FROM match WHERE id = ?",
            ("m-1",),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["table_number"] == 1
        assert row["is_feature_match"] == 1
    finally:
        connection.close()
