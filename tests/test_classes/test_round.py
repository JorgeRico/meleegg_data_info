"""Tests for Round class."""

from classes.Round import Round
from classes.db import Db


def test_round_creation(sample_round):
    assert sample_round.id == 5001
    assert sample_round.name == "Round 1"


def test_round_from_dict():
    data = {"round_id": "5002", "round_name": "Round 2", "is_completed": True}
    r = Round.from_dict(data)
    assert r.id == 5002
    assert r.name == "Round 2"


def test_round_insert_all(temp_db):
    db = Db()
    connection = db.get_connection()
    try:
        r = Round(id=5001, name="Round 1")
        Round.insert_all(connection, [r])
        connection.commit()

        cursor = connection.execute(
            "SELECT id, name FROM round WHERE id = ?", (5001,)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["id"] == 5001
        assert row["name"] == "Round 1"
    finally:
        connection.close()
