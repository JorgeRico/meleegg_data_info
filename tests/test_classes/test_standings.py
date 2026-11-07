"""Tests for Standings class."""

from classes.Standings import PAGE_SIZE, Standings
from classes.db import Db


def test_standings_creation(sample_standings):
    assert sample_standings.id == 1001
    assert sample_standings.id_round == 5001
    assert sample_standings.id_player_1 == 4001
    assert sample_standings.id_player_2 == 0
    assert sample_standings.player_1_wins == 1
    assert sample_standings.player_2_wins == 0
    assert sample_standings.text_result == "1-0-0"


def test_standings_insert_all(temp_db):
    db = Db()
    connection = db.get_connection()
    try:
        # Insert player first (foreign key)
        connection.execute(
            "INSERT INTO player (id, team_id, display_name, username, decklist_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (4001, 7001, "Alice", "alice", None),
        )
        # Insert round first (foreign key)
        connection.execute("INSERT INTO round (id, name) VALUES (?, ?)", (5001, "Round 1"))
        connection.commit()

        standings_data = {
            "id_player": 4001,
            "id_round": 5001,
            "match_record": "1-0-0",
            "game_record": "2-0-0",
            "points": 3,
        }
        Standings.insert_all(connection, [standings_data])
        connection.commit()

        cursor = connection.execute(
            "SELECT id_player, id_round, match_record, game_record, points "
            "FROM standings WHERE id_player = ? AND id_round = ?",
            (4001, 5001),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["match_record"] == "1-0-0"
        assert row["game_record"] == "2-0-0"
        assert row["points"] == 3
    finally:
        connection.close()


def test_fetch_round_standings_pagination():
    """Test fetch_round_standings paginates through multiple pages."""
    class FakeSession:
        def __init__(self):
            self.call_count = 0

        def post(self, url, data, timeout=60):
            self.call_count += 1
            class FakeResponse:
                def __init__(self, data):
                    self._data = data
                def raise_for_status(self):
                    pass
                def json(self):
                    return self._data
            if self.call_count == 1:
                # Return exactly PAGE_SIZE items to trigger another page request
                return FakeResponse({"data": [{"ID": i} for i in range(PAGE_SIZE)]})
            else:
                return FakeResponse({"data": []})

    session = FakeSession()
    result = Standings.fetch_round_standings(session, "5001")
    assert len(result) == PAGE_SIZE
    assert session.call_count == 2  # First page (PAGE_SIZE items) + empty page to stop


def test_fetch_round_matches_pagination():
    """Test fetch_round_matches paginates through multiple pages."""
    class FakeSession:
        def __init__(self):
            self.call_count = 0

        def post(self, url, data, headers=None, timeout=60):
            self.call_count += 1
            class FakeResponse:
                def __init__(self, status_code, data):
                    self.status_code = status_code
                    self._data = data
                def raise_for_status(self):
                    pass
                def json(self):
                    return self._data
            if self.call_count == 1:
                # Return exactly PAGE_SIZE items to trigger another page request
                return FakeResponse(200, {"data": [{"Guid": f"m-{i}"} for i in range(PAGE_SIZE)]})
            else:
                return FakeResponse(200, {"data": []})

    session = FakeSession()
    result = Standings.fetch_round_matches(session, "5001")
    assert len(result) == PAGE_SIZE
    assert session.call_count == 2


def test_fetch_round_matches_error_breaks():
    """Test fetch_round_matches stops on error status."""
    class FakeSession:
        def post(self, url, data, headers=None, timeout=60):
            class FakeResponse:
                def __init__(self, status_code, data=None):
                    self.status_code = status_code
                    self._data = data or {}
                def raise_for_status(self):
                    pass
                def json(self):
                    return self._data
            return FakeResponse(500, {})

    session = FakeSession()
    result = Standings.fetch_round_matches(session, "5001")
    assert result == []
