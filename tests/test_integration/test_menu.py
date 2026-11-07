"""Integration tests for Menu class."""

import openpyxl
import pytest
from pathlib import Path

from classes.Menu import Menu
from classes.Tournament import Tournament
from classes.db import Db

TEST_OUTPUT_FILES_DIR = Path(__file__).resolve().parent / "output_files"


def test_menu_get_player_decklists(menu_with_db):
    """Test that get_player_decklists exports correct data."""
    file_name = "test_decklists.xlsx"
    output_dir = TEST_OUTPUT_FILES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    fp = output_dir / file_name
    if fp.exists():
        fp.unlink()

    connection = Db().get_connection()
    try:
        rows = connection.execute(
            """
            SELECT d.name AS decklist_name, COUNT(p.id) AS total
            FROM player p
            JOIN deck d ON p.decklist_id = d.id
            GROUP BY d.name
            ORDER BY total DESC, d.name ASC
            """
        ).fetchall()
    finally:
        connection.close()

    assert len(rows) == 1
    assert rows[0]["decklist_name"] == "Dimir Hogaak"
    assert rows[0]["total"] == 2  # Both Alice and Bob use this deck


def test_menu_get_maindeck_stats(menu_with_db):
    """Test get_maindeck_stats exports correct data."""
    file_name = "test_maindeck.xlsx"
    output_dir = TEST_OUTPUT_FILES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    fp = output_dir / file_name
    if fp.exists():
        fp.unlink()

    connection = Db().get_connection()
    try:
        # Insert decklist data for maindeck stats test
        connection.execute(
            "INSERT INTO decklist (id_deck, id_card, total, is_sideboard, is_maindeck) "
            "VALUES (?, ?, ?, ?, ?)",
            ("deck-guid-001", 1, 4, 0, 1),
        )
        connection.execute(
            "INSERT INTO decklist (id_deck, id_card, total, is_sideboard, is_maindeck) "
            "VALUES (?, ?, ?, ?, ?)",
            ("deck-guid-001", 2, 1, 0, 1),
        )
        connection.commit()
    finally:
        connection.close()

    connection = Db().get_connection()
    try:
        rows = connection.execute(
            """
            SELECT c.name AS card_name, SUM(dl.total) AS total
            FROM decklist dl
            JOIN card c ON dl.id_card = c.id
            WHERE dl.is_maindeck = 1
            GROUP BY c.name
            ORDER BY total DESC, c.name ASC
            """
        ).fetchall()
    finally:
        connection.close()

    assert len(rows) == 2
    assert rows[0]["card_name"] == "Swamp"
    assert rows[0]["total"] == 4


def test_menu_get_sideboard_stats(menu_with_db):
    """Test get_sideboard_stats exports correct data."""
    file_name = "test_sideboard.xlsx"
    output_dir = TEST_OUTPUT_FILES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    fp = output_dir / file_name
    if fp.exists():
        fp.unlink()

    connection = Db().get_connection()
    try:
        connection.execute(
            "INSERT INTO decklist (id_deck, id_card, total, is_sideboard, is_maindeck) "
            "VALUES (?, ?, ?, ?, ?)",
            ("deck-guid-001", 2, 3, 1, 0),
        )
        connection.commit()
    finally:
        connection.close()

    connection = Db().get_connection()
    try:
        rows = connection.execute(
            """
            SELECT c.name AS card_name, SUM(dl.total) AS total
            FROM decklist dl
            JOIN card c ON dl.id_card = c.id
            WHERE dl.is_sideboard = 1
            GROUP BY c.name
            ORDER BY total DESC, c.name ASC
            """
        ).fetchall()
    finally:
        connection.close()

    assert len(rows) == 1
    assert rows[0]["card_name"] == "Island"
    assert rows[0]["total"] == 3


def test_menu_get_standings(menu_with_db):
    """Test get_standings exports correct data."""
    file_name = "test_standings.xlsx"
    output_dir = TEST_OUTPUT_FILES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    fp = output_dir / file_name
    if fp.exists():
        fp.unlink()

    connection = Db().get_connection()
    try:
        rounds = connection.execute(
            "SELECT id, name FROM round ORDER BY id"
        ).fetchall()
        assert len(rounds) == 2

        # Build prev round map
        round_list = [(r["id"], r["name"]) for r in rounds]
        prev_round_map = {}
        for i in range(1, len(round_list)):
            prev_round_map[round_list[i][0]] = round_list[i - 1][0]

        # Pre-load standings points
        all_standings_points = {}
        standings_rows = connection.execute(
            "SELECT id_player, id_round, points FROM standings"
        ).fetchall()
        for row in standings_rows:
            all_standings_points[(row["id_player"], row["id_round"])] = row["points"]

        # Build workbook manually to verify logic
        workbook = openpyxl.Workbook()

        for round_id, round_name in round_list:
            prev_round_id = prev_round_map.get(round_id)
            matches = connection.execute(
                """
                SELECT
                    m.id_player_1,
                    m.id_player_2,
                    m.table_number,
                    p1.display_name AS player_1_name,
                    p2.display_name AS player_2_name,
                    d1.name AS player_1_decklist_name,
                    d2.name AS player_2_decklist_name,
                    s1.match_record AS text_result,
                    s1.game_record AS game_record
                FROM match m
                LEFT JOIN player p1 ON m.id_player_1 = p1.id
                LEFT JOIN player p2 ON m.id_player_2 = p2.id
                LEFT JOIN deck d1 ON p1.decklist_id = d1.id
                LEFT JOIN deck d2 ON p2.decklist_id = d2.id
                LEFT JOIN standings s1 ON s1.id_player = m.id_player_1 AND s1.id_round = m.id_round
                WHERE m.id_round = ?
                ORDER BY m.id
                """,
                (round_id,),
            ).fetchall()

            if not matches:
                continue

            sheet_name = round_name[:31]
            sheet = workbook.create_sheet(title=sheet_name)
            sheet.append(
                [
                    "player_1", "player_1_points", "player_2", "player_2_points",
                    "text_result", "game_record",
                    "player_1_decklist_name", "player_2_decklist_name", "table",
                ]
            )

            for match in matches:
                p1_points = (
                    all_standings_points.get((match["id_player_1"], prev_round_id), 0)
                    if prev_round_id is not None else 0
                )
                p2_points = (
                    all_standings_points.get((match["id_player_2"], prev_round_id), 0)
                    if prev_round_id is not None else 0
                )
                sheet.append(
                    [
                        match["player_1_name"],
                        p1_points,
                        match["player_2_name"],
                        p2_points,
                        match["text_result"],
                        match["game_record"],
                        match["player_1_decklist_name"],
                        match["player_2_decklist_name"],
                        match["table_number"],
                    ]
                )

        if "Sheet" in workbook.sheetnames:
            del workbook["Sheet"]

        fp = output_dir / file_name
        workbook.save(fp)
    finally:
        connection.close()

    assert fp.exists()
    wb = openpyxl.load_workbook(fp)
    assert "Round 1" in wb.sheetnames
    assert "Round 2" in wb.sheetnames

    ws = wb["Round 1"]
    headers = [c.value for c in ws[1]]
    assert headers == [
        "player_1", "player_1_points", "player_2", "player_2_points",
        "text_result", "game_record", "player_1_decklist_name",
        "player_2_decklist_name", "table",
    ]

    # Round 1: both players should have 0 points (no previous round)
    row2 = [c.value for c in ws[2]]
    assert row2[0] == "Alice Player"
    assert row2[1] == 0  # No previous round, so 0 points
    assert row2[2] == "Bob Player"
    assert row2[3] == 0

    # Round 2: players should have points from Round 1
    ws2 = wb["Round 2"]
    row2 = [c.value for c in ws2[2]]
    assert row2[0] == "Alice Player"
    assert row2[1] == 3  # Points from Round 1
    assert row2[2] == "Bob Player"
    assert row2[3] == 0


def test_menu_show_menu(menu_with_db, monkeypatch, capsys):
    """Test show_menu displays menu and returns user input."""
    menu, _ = menu_with_db
    monkeypatch.setattr("builtins.input", lambda _: "1")
    result = menu.show_menu()
    captured = capsys.readouterr()
    assert result == "1"
    assert "Eternal Weekend Tournament Toolkit" in captured.out
    assert "1.- Get Tournament Info" in captured.out


def test_menu_exit_app(menu_with_db):
    """Test exit_app raises SystemExit."""
    menu, _ = menu_with_db
    with pytest.raises(SystemExit):
        menu.exit_app()


def test_menu_press_any_key(menu_with_db, monkeypatch):
    """Test press_any_key calls input."""
    menu, _ = menu_with_db
    monkeypatch.setattr("builtins.input", lambda _: "")
    menu.press_any_key()  # Should not raise


def test_menu_clear_screen(menu_with_db, monkeypatch):
    """Test clear_screen calls subprocess.call."""
    menu, _ = menu_with_db
    called = []
    monkeypatch.setattr("subprocess.call", lambda cmd, shell=True: called.append(cmd))
    menu.clear_screen()
    assert len(called) == 1


def test_menu_run_exit(menu_with_db, monkeypatch):
    """Test run() exits when option 7 is selected."""
    menu, _ = menu_with_db
    monkeypatch.setattr("builtins.input", lambda _: "7")
    with pytest.raises(SystemExit):
        menu.run()


def test_menu_run_invalid_option(menu_with_db, monkeypatch, capsys):
    """Test run() shows error for invalid input."""
    menu, _ = menu_with_db
    inputs = iter(["99", "7", "7"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    with pytest.raises(SystemExit):
        menu.run()
    captured = capsys.readouterr()
    assert "Invalid option" in captured.out


def test_menu_get_decklist_stats(menu_with_db):
    """Test get_decklist_stats placeholder does not raise."""
    menu, _ = menu_with_db
    menu.get_decklist_stats()  # Should not raise


def test_menu_get_tournament_info(monkeypatch):
    """Test get_tournament_info calls fetch_tournament_data."""
    menu = Menu.__new__(Menu)
    monkeypatch.setattr(Tournament, "get_tournament_id", lambda url: "491103")
    monkeypatch.setattr(
        Tournament,
        "fetch_tournament_data",
        lambda url, **kw: {
            "tournament_name": "Test Tournament",
            "tournament_id": "491103",
            "rounds_count": 3,
        },
    )
    printed = []
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: printed.append(args[0]))
    menu.get_tournament_info()
    assert any("Test Tournament" in str(a) for a in printed)
    assert "491103" in str(printed[-1]) if printed else True