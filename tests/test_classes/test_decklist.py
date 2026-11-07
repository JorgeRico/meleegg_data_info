"""Tests for Decklist class."""

from classes.Decklist import Decklist
from classes.db import Db


def test_decklist_creation(sample_decklist):
    assert sample_decklist.id == 1
    assert sample_decklist.id_deck == "deck-guid-001"
    assert sample_decklist.id_card == 1
    assert sample_decklist.total == 4
    assert sample_decklist.is_sideboard is False
    assert sample_decklist.is_maindeck is True


def test_decklist_from_decklist_details(sample_deck_details):
    name_to_id = {"Stitcher's Supplier": 1, "Swamp": 2}
    decklists = Decklist.from_decklist_details(
        "deck-guid-001", sample_deck_details, name_to_id
    )
    assert len(decklists) == 2

    maindeck = [dl for dl in decklists if dl.is_maindeck]
    sideboard = [dl for dl in decklists if dl.is_sideboard]

    assert len(maindeck) == 2
    assert maindeck[0].id_deck == "deck-guid-001"
    assert maindeck[0].id_card == 1  # Stitcher's Supplier
    assert maindeck[0].total == 4
    assert maindeck[1].id_card == 2  # Swamp
    assert maindeck[1].total == 1


def test_decklist_from_decklist_details_unknown_card():
    details = {
        "Records": [{"n": "Unknown Card", "q": 2, "c": 0, "t": "Creature"}]
    }
    decklists = Decklist.from_decklist_details("deck-1", details, {})
    assert decklists == []


def test_decklist_insert_all(temp_db):
    db = Db()
    connection = db.get_connection()
    try:
        # Insert a deck first (foreign key)
        connection.execute(
            "INSERT INTO deck (id, name) VALUES (?, ?)", ("deck-1", "Test Deck")
        )
        connection.execute(
            "INSERT INTO card (id, name) VALUES (?, ?)", (1, "Swamp")
        )
        connection.commit()

        dl = Decklist(
            id=1, id_deck="deck-1", id_card=1, total=4,
            is_sideboard=False, is_maindeck=True,
        )
        Decklist.insert_all(connection, [dl])
        connection.commit()

        cursor = connection.execute(
            "SELECT id_deck, id_card, total FROM decklist WHERE id = ?", (1,)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["id_deck"] == "deck-1"
        assert row["id_card"] == 1
        assert row["total"] == 4
    finally:
        connection.close()
