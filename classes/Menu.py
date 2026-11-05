import os
import subprocess
import sys

from classes.Tournament import DEFAULT_TOURNAMENT_URL, Tournament


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
        from classes.db import Db
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
        print("Get Player Decklists\n")

    def get_decklist_stats(self):
        print("Get Decklist Stats\n")

    def get_standings(self):
        print("Get Standings\n")

    def get_maindeck_stats(self):
        print("Get Maindeck Stats\n")

    def get_sideboard_stats(self):
        print("Get Sideboard Stats\n")

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
