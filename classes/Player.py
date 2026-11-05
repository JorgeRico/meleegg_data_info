class Player:
    def __init__(self, id: int, team_id: int, display_name: str, username: str, decklist_id: str = None):
        self.id = id
        self.team_id = team_id
        self.display_name = display_name
        self.username = username
        self.decklist_id = decklist_id

    @classmethod
    def from_standings(cls, standings: list) -> dict:
        """Extract unique players from standings data."""
        players = {}
        for standing in standings:
            team = standing.get("Team") or {}
            decklist_map = {}
            for dl in standing.get("Decklists", []) or []:
                decklist_map[dl.get("PlayerId")] = dl.get("DecklistId")
            for player in team.get("Players", []) or []:
                players[player["ID"]] = cls(
                    id=player["ID"],
                    team_id=player["TeamId"],
                    display_name=player.get("DisplayName", ""),
                    username=player.get("Username", ""),
                    decklist_id=decklist_map.get(player["ID"]),
                )
        return players

    @classmethod
    def insert_all(cls, connection, players) -> None:
        connection.executemany(
            """
            INSERT OR IGNORE INTO player (id, team_id, display_name, username, decklist_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(p.id, p.team_id, p.display_name, p.username, p.decklist_id) for p in players],
        )
        connection.commit()
