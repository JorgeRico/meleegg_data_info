"""Shared fixtures and test configuration."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from classes.Card import Card
from classes.Deck import Deck
from classes.Decklist import Decklist
from classes.Match import Match
from classes.Menu import Menu
from classes.Player import Player
from classes.Round import Round
from classes.Standings import Standings
from classes.db import Db
import classes.db.db as db_module


# ---------------------------------------------------------------------------
# Sample data fixtures (minimal, self-contained)
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_standings_round_data():
    """A single round's standings API response (2 players)."""
    return [
        {
            "ID": 1001,
            "RoundId": 5001,
            "RoundNumber": 1,
            "Team": {
                "ID": 7001,
                "Name": None,
                "Players": [
                    {
                        "ID": 4001,
                        "TeamId": 7001,
                        "ScreenName": "N/A",
                        "DisplayName": "Alice Player",
                        "Username": "alice",
                        "TeamId": 7001,
                    }
                ],
            },
            "MatchWins": 1,
            "MatchLosses": 0,
            "MatchRecord": "1-0-0",
            "GameWins": 2,
            "GameLosses": 0,
            "GameRecord": "2-0-0",
            "Points": 3,
            "Rank": 1,
        },
        {
            "ID": 1002,
            "RoundId": 5001,
            "RoundNumber": 1,
            "Team": {
                "ID": 7002,
                "Name": None,
                "Players": [
                    {
                        "ID": 4002,
                        "TeamId": 7002,
                        "ScreenName": "N/A",
                        "DisplayName": "Bob Player",
                        "Username": "bob",
                        "TeamId": 7002,
                    }
                ],
            },
            "MatchWins": 0,
            "MatchLosses": 1,
            "MatchRecord": "0-1-0",
            "GameWins": 0,
            "GameLosses": 2,
            "GameRecord": "0-2-0",
            "Points": 0,
            "Rank": 2,
        },
    ]


@pytest.fixture
def sample_match_data():
    """A single round's matches API response (1 match)."""
    return [
        {
            "Guid": "abc-123-def-456",
            "RoundId": 5001,
            "RoundNumber": 1,
            "TableNumber": 4,
            "ResultString": "Alice Player won 2-0-0",
            "Competitors": [
                {
                    "ID": 9001,
                    "TeamId": 7001,
                    "Team": {
                        "Players": [
                            {
                                "ID": 4001,
                                "TeamId": 7001,
                                "DisplayName": "Alice Player",
                                "Username": "alice",
                            }
                        ]
                    },
                    "GameWins": 2,
                },
                {
                    "ID": 9002,
                    "TeamId": 7002,
                    "Team": {
                        "Players": [
                            {
                                "ID": 4002,
                                "TeamId": 7002,
                                "DisplayName": "Bob Player",
                                "Username": "bob",
                            }
                        ]
                    },
                    "GameWins": 0,
                },
            ],
        }
    ]


@pytest.fixture
def sample_deck_details():
    """A single decklist details API response."""
    return {
        "Guid": "deck-guid-001",
        "DecklistName": "Dimir Hogaak",
        "FormatName": "Legacy",
        "Records": [
            {"l": "stitcherssupplier", "n": "Stitcher's Supplier", "q": 4, "c": 0, "t": "Creature"},
            {"l": "swamp", "n": "Swamp", "q": 1, "c": 0, "t": "Land"},
        ],
    }


@pytest.fixture
def sample_rounds():
    """Sample tournament rounds."""
    return [
        {"round_id": "5001", "round_name": "Round 1", "is_completed": True},
        {"round_id": "5002", "round_name": "Round 2", "is_completed": True},
        {"round_id": "5003", "round_name": "Round 3", "is_completed": False},
    ]


# ---------------------------------------------------------------------------
# Temporary directories / files
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def temp_db(temp_dir):
    """Create a temporary SQLite database and initialize schema."""
    db_path = temp_dir / "test.db"
    original_path = db_module.DATABASE_PATH
    db_module.DATABASE_PATH = db_path

    db = Db()
    db.init_database()

    yield db_path

    db_module.DATABASE_PATH = original_path


# ---------------------------------------------------------------------------
# Model instance fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_card():
    return Card(id=1, name="Swamp")


@pytest.fixture
def sample_deck():
    return Deck(id="deck-guid-001", name="Dimir Hogaak")


@pytest.fixture
def sample_decklist():
    return Decklist(
        id=1,
        id_deck="deck-guid-001",
        id_card=1,
        total=4,
        is_sideboard=False,
        is_maindeck=True,
    )


@pytest.fixture
def sample_player():
    return Player(
        id=4001,
        team_id=7001,
        display_name="Alice Player",
        username="alice",
        decklist_id="deck-guid-001",
    )


@pytest.fixture
def sample_round():
    return Round(id=5001, name="Round 1")


@pytest.fixture
def sample_match():
    return Match(
        id="abc-123-def-456",
        id_round=5001,
        id_player_1=4001,
        id_player_2=4002,
        player_1_wins=2,
        player_2_wins=0,
        text_result="Alice Player won 2-0-0",
        table_number=4,
        is_feature_match=0,
    )


@pytest.fixture
def sample_standings():
    return Standings(
        id=1001,
        id_round=5001,
        id_player_1=4001,
        id_player_2=0,
        player_1_wins=1,
        player_2_wins=0,
        text_result="1-0-0",
    )


# ---------------------------------------------------------------------------
# Helper: create a fresh in-memory DB for Menu tests
# ---------------------------------------------------------------------------


@pytest.fixture
def menu_with_db(temp_dir):
    """Create a Menu instance connected to a temp DB with seed data."""
    db_path = temp_dir / "menu_test.db"
    original_path = db_module.DATABASE_PATH
    db_module.DATABASE_PATH = db_path

    db = Db()
    db.init_database()

    connection = db.get_connection()
    try:
        connection.execute(
            "INSERT INTO deck (id, name) VALUES (?, ?)",
            ("deck-guid-001", "Dimir Hogaak"),
        )
        connection.execute("INSERT INTO card (id, name) VALUES (?, ?)", (1, "Swamp"))
        connection.execute("INSERT INTO card (id, name) VALUES (?, ?)", (2, "Island"))
        connection.execute(
            "INSERT INTO player (id, team_id, display_name, username, decklist_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (4001, 7001, "Alice Player", "alice", "deck-guid-001"),
        )
        connection.execute(
            "INSERT INTO player (id, team_id, display_name, username, decklist_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (4002, 7002, "Bob Player", "bob", "deck-guid-001"),
        )
        connection.execute("INSERT INTO round (id, name) VALUES (?, ?)", (5001, "Round 1"))
        connection.execute("INSERT INTO round (id, name) VALUES (?, ?)", (5002, "Round 2"))
        connection.execute(
            "INSERT INTO match (id, id_round, id_player_1, id_player_2, "
            "player_1_wins, player_2_wins, text_result, table_number, is_feature_match) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("m-1", 5001, 4001, 4002, 2, 0, "Alice won 2-0-0", 1, 0),
        )
        connection.execute(
            "INSERT INTO match (id, id_round, id_player_1, id_player_2, "
            "player_1_wins, player_2_wins, text_result, table_number, is_feature_match) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("m-2", 5002, 4001, 4002, 1, 1, "Alice won 2-1-0", 2, 0),
        )
        connection.execute(
            "INSERT INTO standings (id_player, id_round, match_record, game_record, points) "
            "VALUES (?, ?, ?, ?, ?)",
            (4001, 5001, "1-0-0", "2-0-0", 3),
        )
        connection.execute(
            "INSERT INTO standings (id_player, id_round, match_record, game_record, points) "
            "VALUES (?, ?, ?, ?, ?)",
            (4002, 5001, "0-1-0", "0-2-0", 0),
        )
        connection.execute(
            "INSERT INTO standings (id_player, id_round, match_record, game_record, points) "
            "VALUES (?, ?, ?, ?, ?)",
            (4001, 5002, "2-0-0", "4-0-0", 6),
        )
        connection.execute(
            "INSERT INTO standings (id_player, id_round, match_record, game_record, points) "
            "VALUES (?, ?, ?, ?, ?)",
            (4002, 5002, "0-2-0", "0-4-0", 0),
        )
        connection.commit()
    finally:
        connection.close()

    menu = Menu()
    yield menu, db_path

    db_module.DATABASE_PATH = original_path
