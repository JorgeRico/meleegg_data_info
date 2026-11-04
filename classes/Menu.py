import os
import subprocess
import sys

from helpers.db import init_database

DEFAULT_TOURNAMENT_URL = "https://melee.gg/Tournament/View/491103#standings"

MENU = """
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


def show_menu():
    print(MENU)
    return input("Select an option: ").strip()


def get_tournament_info():
    print("\n - Get Tournament Info")


def get_player_decklists():
    print("\n - Get Player Decklists")


def get_decklist_stats():
    print("\n - Get Decklist Stats")


def get_standings():
    print("\n - Get Standings")


def get_maindeck_stats():
    print("\n - Get Maindeck Stats")


def get_sideboard_stats():
    print("\n - Get Sideboard Stats")


def exit_app():
    print("Exit\n")
    sys.exit(0)


def press_any_key():
    input("\nPress any key to return to menu...")


def clear_screen():
    subprocess.call("cls" if os.name == "nt" else "clear", shell=True)


def menu():
    init_database()
    while True:
        option = show_menu()
        match option:
            case "7":
                exit_app()
            case "1":
                get_tournament_info()
            case "2":
                get_player_decklists()
            case "3":
                get_decklist_stats()
            case "4":
                get_standings()
            case "5":
                get_maindeck_stats()
            case "6":
                get_sideboard_stats()
            case _:
                print("Invalid option\n")
                continue
        press_any_key()
        clear_screen()
