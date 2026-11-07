from classes.Deck import Deck
from classes.db import Db


def test_deck_creation(sample_deck):
    assert sample_deck.id == "deck-guid-001"
    assert sample_deck.name == "Dimir Hogaak"


def test_deck_from_standings_data(sample_standings_round_data):
    decks = Deck.from_standings_data(sample_standings_round_data)
    # Standings data doesn't contain Decklists in this fixture
    assert decks == {}


def test_deck_from_standings_data_with_decklists():
    standings = [
        {
            "ID": 1001,
            "RoundId": 5001,
            "Decklists": [
                {
                    "DecklistId": "deck-uuid-1",
                    "PlayerId": 4001,
                    "DecklistName": "Dimir Hogaak",
                    "Format": "Legacy",
                }
            ],
            "Team": {"Players": [{"ID": 4001, "TeamId": 7001}]},
        }
    ]
    decks = Deck.from_standings_data(standings)
    assert len(decks) == 1
    assert "deck-uuid-1" in decks
    assert decks["deck-uuid-1"].id == "deck-uuid-1"
    assert decks["deck-uuid-1"].name == "Dimir Hogaak"


def test_deck_insert_all(temp_db):
    db = Db()
    connection = db.get_connection()
    try:
        deck = Deck(id="deck-1", name="Test Deck")
        Deck.insert_all(connection, {"deck-1": deck})
        connection.commit()

        cursor = connection.execute("SELECT id, name FROM deck WHERE id = ?", ("deck-1",))
        row = cursor.fetchone()
        assert row is not None
        assert row["id"] == "deck-1"
        assert row["name"] == "Test Deck"
    finally:
        connection.close()


def test_deck_insert_all_duplicate(temp_db):
    from classes.db import Db

    db = Db()
    connection = db.get_connection()
    try:
        Deck.insert_all(connection, {"deck-1": Deck(id="deck-1", name="Deck One")})
        Deck.insert_all(connection, {"deck-1": Deck(id="deck-1", name="Deck Two")})
        connection.commit()

        cursor = connection.execute("SELECT name FROM deck WHERE id = ?", ("deck-1",))
        row = cursor.fetchone()
        assert row["name"] == "Deck One"  # INSERT OR IGNORE keeps first
    finally:
        connection.close()
