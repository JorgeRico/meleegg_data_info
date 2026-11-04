from pathlib import Path

from openpyxl import Workbook

OUTPUT_FILES_DIR = Path(__file__).resolve().parent


def export_decklists_to_excel(decklists, file_name: str = "decklists.xlsx") -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["id_deck", "id_card", "total", "is_sideboard", "is_maindeck"])
    for decklist in decklists:
        sheet.append(
            [
                decklist["id_deck"],
                decklist["id_card"],
                decklist["total"],
                decklist["is_sideboard"],
                decklist["is_maindeck"],
            ]
        )
    file_path = OUTPUT_FILES_DIR / file_name
    workbook.save(file_path)
    return file_path


def export_standings_to_excel(standings, file_name: str = "standings.xlsx") -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["id_round", "id_player_1", "id_player_2", "player_1_wins", "player_2_wins", "text_result"])
    for standing in standings:
        sheet.append(
            [
                standing["id_round"],
                standing["id_player_1"],
                standing["id_player_2"],
                standing["player_1_wins"],
                standing["player_2_wins"],
                standing["text_result"],
            ]
        )
    file_path = OUTPUT_FILES_DIR / file_name
    workbook.save(file_path)
    return file_path
