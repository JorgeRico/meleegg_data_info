import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from classes.Card import Card
from classes.Deck import Deck
from classes.Decklist import Decklist
from classes.Match import Match
from classes.Player import Player
from classes.Round import Round
from classes.Standings import Standings
from classes.db import Db

DEFAULT_TOURNAMENT_URL = "https://melee.gg/Tournament/View/491103#standings"

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = ROOT_DIR / "raw_data"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

DECKLIST_DETAILS_URL = "https://melee.gg/Decklist/GetDecklistDetails"


class Tournament:
    def __init__(self, id: str, name: str = None, url: str = None):
        self.id = id
        self.name = name
        self.url = url

    @classmethod
    def get_tournament_id(cls, url: str) -> str:
        match = re.search(r"/Tournament/View/(\d+)", url)
        if match is None:
            raise ValueError(f"Invalid tournament url: {url}")
        return match.group(1)

    @classmethod
    def _build_session(cls) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Origin": "https://melee.gg",
                "Referer": "https://melee.gg/",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            }
        )
        return session

    @classmethod
    def _extract_tournament_page(cls, url: str) -> dict:
        """Fetch the tournament page with requests and extract metadata + rounds using BeautifulSoup."""
        tournament_id = cls.get_tournament_id(url)
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})
        response = session.get(url, timeout=60)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else None
        tournament_name = title.split(" | ")[0].strip() if title else None

        rounds = []
        seen = set()
        for el in soup.select(".round-selector"):
            rid = el.get("data-id")
            if rid and rid not in seen:
                seen.add(rid)
                rounds.append(
                    {
                        "round_id": rid,
                        "round_name": el.get("data-name"),
                        "is_completed": el.get("data-is-completed") == "True",
                    }
                )

        return {
            "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "url": url,
            "rounds": rounds,
        }

    @classmethod
    def fetch_tournament_data(
        cls, url: str = DEFAULT_TOURNAMENT_URL, file_name: Optional[str] = None
    ) -> dict:
        tournament_id = cls.get_tournament_id(url)
        file_name = file_name if file_name is not None else f"tournament_{tournament_id}.json"

        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        Db().init_database()

        page_info = cls._extract_tournament_page(url)
        tournament_name = page_info.get("tournament_name")
        rounds = page_info.get("rounds", [])

        session = cls._build_session()
        enriched_rounds = []
        round_objects = []
        players = {}
        all_matches = []
        all_player_standings = []
        decks = {}
        print("\n - Fetching round data...")
        all_player_standings = cls.fetch_all_round_standings(
            session, rounds, enriched_rounds, round_objects, players, decks
        )

        # Fetch matches using the same requests session
        print("\n - Fetching match data...")
        all_matches.extend(cls.fetch_all_round_matches(session, rounds))

        print(f"\n - Fetching decklist details for {len(decks)} decks...")
        deck_details = cls.fetch_all_decklist_details(session, decks)

        data = {
            "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "rounds_count": len(enriched_rounds),
            "rounds": enriched_rounds,
        }

        connection = Db().get_connection()
        try:
            cls.save_to_database(
                connection, round_objects, decks, deck_details,
                players, all_player_standings, all_matches
            )
        finally:
            connection.close()

        output_path = RAW_DATA_DIR / file_name
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f" - Tournament data saved to {output_path}")
        return data

    @classmethod
    def fetch_all_decklist_details(cls, session: requests.Session, decks: dict) -> dict:
        """Fetch card details for all decks."""
        deck_details = {}
        for deck_id in decks:
            try:
                details = session.get(f"{DECKLIST_DETAILS_URL}/{deck_id}", timeout=60)
                details.raise_for_status()
                deck_details[deck_id] = details.json()
            except Exception as e:
                print(f"  Failed to fetch decklist {deck_id}: {e}")
        return deck_details

    @classmethod
    def save_to_database(
        cls,
        connection,
        round_objects,
        decks,
        deck_details,
        players,
        all_player_standings,
        all_matches,
    ) -> None:
        """Save all tournament data to the database."""
        Round.insert_all(connection, round_objects)
        Deck.insert_all(connection, decks)

        all_cards = {}
        for details in deck_details.values():
            all_cards.update(Card.from_decklist_records(details.get("Records", [])))
        name_to_id = Card.insert_all(connection, all_cards)

        all_decklists = []
        for deck_id, details in deck_details.items():
            all_decklists.extend(
                Decklist.from_decklist_details(deck_id, details, name_to_id)
            )
        Decklist.insert_all(connection, all_decklists)

        Player.insert_all(connection, list(players.values()))
        Standings.insert_all(connection, all_player_standings)
        Match.insert_all(connection, all_matches)

    @classmethod
    def fetch_all_round_standings(
        cls,
        session: requests.Session,
        rounds: list,
        enriched_rounds: list,
        round_objects: list,
        players: dict,
        decks: dict,
    ) -> list:
        """Fetch standings data for all rounds."""
        all_player_standings = []
        print("\n - Fetching round data...")
        for round_info in rounds:
            round_id = round_info["round_id"]
            raw_standings = Standings.fetch_round_standings(session, round_id)
            round_obj = Round.from_dict(round_info)
            round_objects.append(round_obj)
            enriched_rounds.append(
                {
                    **round_info,
                    "standings_count": len(raw_standings),
                    "standings": raw_standings,
                }
            )
            players.update(Player.from_standings(raw_standings))
            decks.update(Deck.from_standings_data(raw_standings))

            for standing in raw_standings:
                team = standing.get("Team") or {}
                team_players = team.get("Players", []) or []
                player_id = team_players[0]["ID"] if team_players else 0
                all_player_standings.append(
                    {
                        "id_player": player_id,
                        "id_round": standing["RoundId"],
                        "match_record": standing.get("MatchRecord", ""),
                        "game_record": standing.get("GameRecord", ""),
                        "points": standing.get("Points", 0),
                    }
                )

            print(
                f"   Round {round_info['round_name']} ({round_id}): "
                f"   {len(raw_standings)} standings fetched"
            )

        return all_player_standings

    @classmethod
    def fetch_all_round_matches(cls, session: requests.Session, rounds: list) -> list:
        """Fetch match data for all rounds using Playwright's APIRequestContext."""
        all_matches = []
        print("\n - Fetching match data...")
        for round_info in rounds:
            round_id = round_info["round_id"]
            try:
                round_matches = Standings.fetch_round_matches(session, round_id)
                match_objects = Match.from_match_data(round_matches)
                all_matches.extend(match_objects)
                print(
                    f"   Round {round_info['round_name']} ({round_id}): "
                    f"   {len(round_matches)} matches fetched"
                )
            except Exception as e:
                print(
                    f"   Round {round_info['round_name']} ({round_id}): "
                    f"   matches unavailable ({e})"
                )
        return all_matches
