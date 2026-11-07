"""Tests for Tournament class."""

from classes.Deck import Deck
from classes.Decklist import Decklist
from classes.Match import Match
from classes.Player import Player
from classes.Round import Round
from classes.Tournament import DEFAULT_TOURNAMENT_URL, Tournament
from classes.db import Db


def test_get_tournament_id_valid():
    url = "https://melee.gg/Tournament/View/491103#standings"
    assert Tournament.get_tournament_id(url) == "491103"


def test_get_tournament_id_no_hash():
    url = "https://melee.gg/Tournament/View/491103"
    assert Tournament.get_tournament_id(url) == "491103"


def test_get_tournament_id_invalid():
    url = "https://melee.gg/Some/Other/Page"
    try:
        Tournament.get_tournament_id(url)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid tournament url" in str(e)


def test_default_tournament_url():
    assert DEFAULT_TOURNAMENT_URL == "https://melee.gg/Tournament/View/491103#standings"


def test_tournament_creation():
    t = Tournament(id="491103", name="Test Tournament", url="https://melee.gg/Tournament/View/491103")
    assert t.id == "491103"
    assert t.name == "Test Tournament"
    assert t.url == "https://melee.gg/Tournament/View/491103"


def test_build_session_headers():
    """Test that _build_session sets correct headers."""
    session = Tournament._build_session()
    assert session.headers["User-Agent"] is not None
    assert session.headers["Origin"] == "https://melee.gg"
    assert session.headers["Referer"] == "https://melee.gg/"
    assert "X-Requested-With" in session.headers
    assert session.headers["X-Requested-With"] == "XMLHttpRequest"
    assert session.headers["Content-Type"] == "application/x-www-form-urlencoded; charset=UTF-8"


def test_fetch_all_round_standings(monkeypatch):
    """Test fetch_all_round_standings collects standings from all rounds."""
    class FakeSession:
        def post(self, url, data, timeout=60):
            class FakeResponse:
                def __init__(self, data):
                    self._data = data
                def raise_for_status(self):
                    pass
                def json(self):
                    return self._data
            return FakeResponse({"data": [{"ID": 1, "RoundId": data["roundId"]}]})

    session = FakeSession()
    rounds = [{"round_id": "5001", "round_name": "Round 1"}, {"round_id": "5002", "round_name": "Round 2"}]
    enriched = []
    round_objects = []
    players = {}
    decks = {}

    result = Tournament.fetch_all_round_standings(session, rounds, enriched, round_objects, players, decks)

    assert len(result) == 2
    assert all(s["id_round"] in ("5001", "5002") for s in result)


def test_fetch_all_round_matches(monkeypatch):
    """Test fetch_all_round_matches collects matches from all rounds."""
    class FakeSession:
        def post(self, url, data, headers=None, timeout=60):
            class FakeResponse:
                def __init__(self, status, data):
                    self.status_code = status
                    self._data = data
                def raise_for_status(self):
                    pass
                def json(self):
                    return self._data
            return FakeResponse(200, {"data": [{"Guid": "m-1", "RoundId": int(data["roundId"])}]})

    session = FakeSession()
    rounds = [{"round_id": "5001", "round_name": "Round 1"}, {"round_id": "5002", "round_name": "Round 2"}]

    result = Tournament.fetch_all_round_matches(session, rounds)

    assert len(result) == 2
    assert result[0].id_round == 5001  # First match from Round 1
    assert result[1].id_round == 5002  # Second match from Round 2


def test_fetch_all_decklist_details(monkeypatch):
    """Test fetch_all_decklist_details collects deck details."""
    class FakeSession:
        def get(self, url, timeout=60):
            class FakeResponse:
                def __init__(self, data):
                    self._data = data
                def raise_for_status(self):
                    pass
                def json(self):
                    return self._data
            return FakeResponse({"Guid": url.split("/")[-1], "DecklistName": "Test Deck"})

    session = FakeSession()
    decks = {"deck-1": Deck(id="deck-1", name="Deck 1")}

    result = Tournament.fetch_all_decklist_details(session, decks)

    assert len(result) == 1
    assert result["deck-1"]["DecklistName"] == "Test Deck"
    assert result["deck-1"]["Guid"] == "deck-1"


def test_save_to_database(temp_db):
    """Test save_to_database persists all data correctly."""
    db = Db()
    connection = db.get_connection()
    try:
        round_objects = [Round(id=5001, name="Round 1")]
        decks = {"deck-1": Deck(id="deck-1", name="Dimir Hogaak")}
        deck_details = {"deck-1": {"Records": [
            {"n": "Swamp", "q": 4, "c": 0, "t": "Land"},
        ]}}
        players = {4001: Player(id=4001, team_id=7001, display_name="Alice", username="alice", decklist_id="deck-guid-001")}
        all_player_standings = [{"id_player": 4001, "id_round": 5001, "match_record": "1-0-0", "game_record": "2-0-0", "points": 3}]
        all_matches = []

        Tournament.save_to_database(connection, round_objects, decks, deck_details, players, all_player_standings, all_matches)

        # Verify rounds inserted
        cur = connection.execute("SELECT COUNT(*) FROM round")
        assert cur.fetchone()[0] == 1

        # Verify decks inserted
        cur = connection.execute("SELECT COUNT(*) FROM deck")
        assert cur.fetchone()[0] == 1

        # Verify cards inserted
        cur = connection.execute("SELECT COUNT(*) FROM card")
        assert cur.fetchone()[0] == 1

        # Verify decklists inserted
        cur = connection.execute("SELECT COUNT(*) FROM decklist")
        assert cur.fetchone()[0] == 1

        # Verify players inserted
        cur = connection.execute("SELECT COUNT(*) FROM player")
        assert cur.fetchone()[0] == 1

        # Verify standings inserted
        cur = connection.execute("SELECT COUNT(*) FROM standings")
        assert cur.fetchone()[0] == 1
    finally:
        connection.close()