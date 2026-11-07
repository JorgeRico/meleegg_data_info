"""Tests for Player class."""

from classes.Player import Player
from classes.db import Db


def test_player_creation(sample_player):
    assert sample_player.id == 4001
    assert sample_player.team_id == 7001
    assert sample_player.display_name == "Alice Player"
    assert sample_player.username == "alice"
    assert sample_player.decklist_id == "deck-guid-001"


def test_player_from_standings(sample_standings_round_data):
    players = Player.from_standings(sample_standings_round_data)
    assert len(players) == 2

    assert 4001 in players
    assert players[4001].display_name == "Alice Player"
    assert players[4001].username == "alice"
    assert players[4001].team_id == 7001
    assert players[4001].decklist_id is None

    assert 4002 in players
    assert players[4002].display_name == "Bob Player"
    assert players[4002].username == "bob"


def test_player_insert_all(temp_db):
    db = Db()
    connection = db.get_connection()
    try:
        player = Player(
            id=4001, team_id=7001, display_name="Alice",
            username="alice", decklist_id="deck-1",
        )
        Player.insert_all(connection, [player])
        connection.commit()

        cursor = connection.execute(
            "SELECT id, display_name, username FROM player WHERE id = ?",
            (4001,),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["display_name"] == "Alice"
        assert row["username"] == "alice"
    finally:
        connection.close()
