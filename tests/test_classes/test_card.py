"""Tests for Card class."""

from classes.Card import Card
from classes.db import Db


def test_card_creation(sample_card):
    assert sample_card.id == 1
    assert sample_card.name == "Swamp"


def test_card_creation_default():
    card = Card(id=42, name="Black Lotus")
    assert card.id == 42
    assert card.name == "Black Lotus"


def test_card_repr():
    card = Card(id=1, name="Swamp")
    assert card.id == 1
    assert card.name == "Swamp"


def test_card_from_decklist_records_empty():
    """Test from_decklist_records with empty list."""
    cards = Card.from_decklist_records([])
    assert cards == {}


def test_card_from_decklist_records_single():
    """Test from_decklist_records with one card record."""
    records = [{"n": "Swamp", "q": 4, "c": 0, "t": "Land"}]
    cards = Card.from_decklist_records(records)
    assert len(cards) == 1
    assert "Swamp" in cards
    assert cards["Swamp"].name == "Swamp"
    assert cards["Swamp"].id is None


def test_card_from_decklist_records_multiple():
    """Test from_decklist_records with multiple card records."""
    records = [
        {"n": "Swamp", "q": 4, "c": 0, "t": "Land"},
        {"n": "Island", "q": 2, "c": 0, "t": "Land"},
        {"n": "Force of Will", "q": 1, "c": 0, "t": "Instant"},
    ]
    cards = Card.from_decklist_records(records)
    assert len(cards) == 3
    assert cards["Swamp"].name == "Swamp"
    assert cards["Island"].name == "Island"
    assert cards["Force of Will"].name == "Force of Will"
    assert all(c.id is None for c in cards.values())


def test_card_from_decklist_records_duplicate_names():
    """Test that duplicate card names are deduplicated."""
    records = [
        {"n": "Swamp", "q": 4, "c": 0, "t": "Land"},
        {"n": "Swamp", "q": 2, "c": 0, "t": "Land"},  # duplicate
    ]
    cards = Card.from_decklist_records(records)
    assert len(cards) == 1
    assert cards["Swamp"].name == "Swamp"


def test_card_from_decklist_records_empty_name():
    """Test that records with empty name are skipped."""
    records = [
        {"n": "", "q": 4, "c": 0, "t": "Land"},
        {"n": "Swamp", "q": 2, "c": 0, "t": "Land"},
    ]
    cards = Card.from_decklist_records(records)
    assert len(cards) == 1
    assert cards["Swamp"].name == "Swamp"


def test_card_insert_all(temp_db):
    """Test insert_all inserts cards into database."""
    db = Db()
    connection = db.get_connection()
    try:
        cards = {"Swamp": Card(id=None, name="Swamp"), "Island": Card(id=None, name="Island")}
        name_to_id = Card.insert_all(connection, cards)
        connection.commit()

        assert len(name_to_id) == 2
        assert name_to_id["Swamp"] == 1
        assert name_to_id["Island"] == 2

        # Verify cards are in database
        cursor = connection.execute("SELECT name FROM card ORDER BY name")
        rows = cursor.fetchall()
        assert [r[0] for r in rows] == ["Island", "Swamp"]
    finally:
        connection.close()


def test_card_insert_all_duplicate(temp_db):
    """Test insert_all is idempotent with INSERT OR IGNORE."""
    db = Db()
    connection = db.get_connection()
    try:
        cards1 = {"Swamp": Card(id=None, name="Swamp")}
        Card.insert_all(connection, cards1)
        connection.commit()

        cards2 = {"Swamp": Card(id=None, name="Swamp")}
        Card.insert_all(connection, cards2)
        connection.commit()

        # Verify only one row exists in the database
        cursor = connection.execute("SELECT COUNT(*) FROM card WHERE name = ?", ("Swamp",))
        count = cursor.fetchone()[0]
        assert count == 1
    finally:
        connection.close()
