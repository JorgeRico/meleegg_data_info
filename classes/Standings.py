import requests

STANDINGS_URL = "https://melee.gg/Standing/GetRoundStandings"
MATCHES_URL = "https://melee.gg/Match/GetRoundMatches"
PAGE_SIZE = 500
MAX_PAGES_PER_ROUND = 1000


class Standings:
    def __init__(self, id: int, id_round: int, id_player_1: int, id_player_2: int, player_1_wins: int, player_2_wins: int, text_result: str):
        self.id = id
        self.id_round = id_round
        self.id_player_1 = id_player_1
        self.id_player_2 = id_player_2
        self.player_1_wins = player_1_wins
        self.player_2_wins = player_2_wins
        self.text_result = text_result

    @staticmethod
    def _datatables_payload(draw: int, start: int, length: int, round_id: str) -> dict:
        payload = {
            "draw": str(draw),
            "start": str(start),
            "length": str(length),
            "search[value]": "",
            "search[regex]": "false",
            "roundId": round_id,
            "columns[0][data]": "rank",
            "columns[0][name]": "",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "team",
            "columns[1][name]": "",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regex]": "false",
            "order[0][column]": "0",
            "order[0][dir]": "asc",
        }
        return payload

    @staticmethod
    def _match_payload(draw: int, start: int, length: int, round_id: str) -> dict:
        payload = {
            "draw": str(draw),
            "start": str(start),
            "length": str(length),
            "search[value]": "",
            "search[regex]": "false",
            "roundId": round_id,
            "columns[0][data]": "TableNumber",
            "columns[0][name]": "",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "PodNumber",
            "columns[1][name]": "",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regex]": "false",
            "order[0][column]": "0",
            "order[0][dir]": "asc",
        }
        return payload

    @classmethod
    def fetch_round_standings(cls, session: requests.Session, round_id: str) -> list:
        """Fetch all standings for a single round using DataTables-style pagination."""
        standings = []
        start = 0
        draw = 1
        for _ in range(MAX_PAGES_PER_ROUND):
            response = session.post(
                STANDINGS_URL, data=cls._datatables_payload(draw, start, PAGE_SIZE, round_id), timeout=60
            )
            response.raise_for_status()
            page_data = response.json()
            page = page_data.get("data", []) or []
            standings.extend(page)
            if len(page) < PAGE_SIZE:
                break
            start += PAGE_SIZE
            draw += 1
        return standings

    @classmethod
    def fetch_round_matches(cls, session: requests.Session, round_id: str) -> list:
        """Fetch all matches for a single round using requests session."""
        matches = []
        start = 0
        draw = 1
        for _ in range(MAX_PAGES_PER_ROUND):
            response = session.post(
                f"{MATCHES_URL}/{round_id}",
                data=cls._match_payload(draw, start, PAGE_SIZE, round_id),
                headers={
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
            if response.status_code >= 400:
                break
            page_data = response.json()
            page = page_data.get("data", []) or []
            matches.extend(page)
            if len(page) < PAGE_SIZE:
                break
            start += PAGE_SIZE
            draw += 1
        return matches
