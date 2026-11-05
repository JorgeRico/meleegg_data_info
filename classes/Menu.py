import os
import subprocess
import sys

from classes.Tournament import DEFAULT_TOURNAMENT_URL, Tournament
from classes.db import Db
from helpers import ExcelHelper
from openpyxl import Workbook


class Menu:
    MENU_TEXT = """
Eternal Weekend Tournament Toolkit
==================================

1.- Get Tournament Info
2.- Get Player Decklists
3.- Get Decklist Stats
4.- Get Standings
5.- Get Maindeck Stats
6.- Get Sideboard Stats

7.- Exit
"""

    def __init__(self):
        Db().init_database()

    def show_menu(self):
        print(self.MENU_TEXT)
        return input("Select an option: ").strip()

    def get_tournament_info(self):
        Tournament.get_tournament_id(DEFAULT_TOURNAMENT_URL)
        data = Tournament.fetch_tournament_data(DEFAULT_TOURNAMENT_URL)
        print(f"\nTournament '{data.get('tournament_name')}' ({data.get('tournament_id')}): "
              f"{data.get('rounds_count')} rounds, saved to raw_data/")

    def get_player_decklists(self):
        file_name = "decklists.xlsx"
        output_dir = ExcelHelper.prepare_output_file(file_name)

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

        if not rows:
            print("No decklist data found.\n")
            return

        data = [[row["decklist_name"], row["total"]] for row in rows]

        file_path = ExcelHelper.export_to_excel(
            data=data,
            headers=["decklist_name", "total"],
            file_name=file_name,
            sheet_name="Decklists",
            output_dir=output_dir,
        )
        print(f"\nDecklists exported to {file_path} ({len(data)} unique decklists)\n")

    def get_decklist_stats(self):
        print("Get Decklist Stats\n")

    def get_standings(self):
        file_name = "standings.xlsx"
        output_dir = ExcelHelper.prepare_output_file(file_name)

        connection = Db().get_connection()
        try:
            rounds = connection.execute(
                "SELECT id, name FROM round ORDER BY id"
            ).fetchall()

            if not rounds:
                print("No round data found.\n")
                return

            # Build previous round mapping
            round_list = [(r["id"], r["name"]) for r in rounds]
            prev_round_map = {}
            for i in range(1, len(round_list)):
                prev_round_map[round_list[i][0]] = round_list[i - 1][0]

            # Pre-load all standings points: (id_player, id_round) -> points
            all_standings_points = {}
            standings_rows = connection.execute(
                "SELECT id_player, id_round, points FROM standings"
            ).fetchall()
            for row in standings_rows:
                all_standings_points[(row["id_player"], row["id_round"])] = row["points"]

            workbook = Workbook()

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
                if sheet_name in workbook.sheetnames:
                    sheet_name = f"{sheet_name[:27]}..."
                sheet = workbook.create_sheet(title=sheet_name)
                sheet.append(
                    [
                        "player_1",
                        "player_1_points",
                        "player_2",
                        "player_2_points",
                        "text_result",
                        "game_record",
                        "player_1_decklist_name",
                        "player_2_decklist_name",
                        "table",
                    ]
                )

                for match in matches:
                    p1_points = (
                        all_standings_points.get((match["id_player_1"], prev_round_id), 0)
                        if prev_round_id is not None
                        else 0
                    )
                    p2_points = (
                        all_standings_points.get((match["id_player_2"], prev_round_id), 0)
                        if prev_round_id is not None
                        else 0
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

            file_path = output_dir / file_name
            workbook.save(file_path)
            print(f"\nStandings exported to {file_path}\n")
        finally:
            connection.close()

    def get_maindeck_stats(self):
        file_name = "maindeck_cards.xlsx"
        output_dir = ExcelHelper.prepare_output_file(file_name)

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

        if not rows:
            print("No maindeck card data found.\n")
            return

        data = [[row["card_name"], row["total"]] for row in rows]

        file_path = ExcelHelper.export_to_excel(
            data=data,
            headers=["card_name", "total"],
            file_name=file_name,
            sheet_name="Maindeck Stats",
            output_dir=output_dir,
        )
        print(f"\nMaindeck stats exported to {file_path} ({len(data)} unique cards)\n")

    def get_sideboard_stats(self):
        file_name = "sideboard_cards.xlsx"
        output_dir = ExcelHelper.prepare_output_file(file_name)

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

        if not rows:
            print("No sideboard card data found.\n")
            return

        data = [[row["card_name"], row["total"]] for row in rows]

        file_path = ExcelHelper.export_to_excel(
            data=data,
            headers=["card_name", "total"],
            file_name=file_name,
            sheet_name="Sideboard Stats",
            output_dir=output_dir,
        )
        print(f"\nSideboard stats exported to {file_path} ({len(data)} unique cards)\n")

    def exit_app(self):
        print("\nExit\n")
        sys.exit(0)

    def press_any_key(self):
        input("Press any key to return to menu...\n")

    def clear_screen(self):
        subprocess.call("cls" if os.name == "nt" else "clear", shell=True)

    def run(self):
        while True:
            option = self.show_menu()
            match option:
                case "7":
                    self.exit_app()
                case "1":
                    self.get_tournament_info()
                case "2":
                    self.get_player_decklists()
                case "3":
                    self.get_decklist_stats()
                case "4":
                    self.get_standings()
                case "5":
                    self.get_maindeck_stats()
                case "6":
                    self.get_sideboard_stats()
                case _:
                    print("Invalid option\n")
                    continue
            self.press_any_key()
            self.clear_screen()


def menu():
    Menu().run()
