class Match:
    def __init__(self, id: str, id_round: int, id_player_1: int, id_player_2: int, player_1_wins: int, player_2_wins: int, text_result: str, table_number: int = None, is_feature_match: int = 0):
        self.id = id
        self.id_round = id_round
        self.id_player_1 = id_player_1
        self.id_player_2 = id_player_2
        self.player_1_wins = player_1_wins
        self.player_2_wins = player_2_wins
        self.text_result = text_result
        self.table_number = table_number
        self.is_feature_match = is_feature_match

    @classmethod
    def from_match_data(cls, matches: list) -> list:
        """Convert API match data into Match objects."""
        results = []
        for m in matches:
            competitors = m.get("Competitors", []) or []
            players = []
            for comp in competitors:
                team = comp.get("Team") or {}
                team_players = team.get("Players", []) or []
                if team_players:
                    players.append(team_players[0]["ID"])
            p1 = players[0] if len(players) > 0 else 0
            p2 = players[1] if len(players) > 1 else 0

            p1_wins = competitors[0].get("GameWins", 0) if len(competitors) > 0 else 0
            p2_wins = competitors[1].get("GameWins", 0) if len(competitors) > 1 else 0

            results.append(cls(
                id=m.get("Guid", ""),
                id_round=m.get("RoundId", 0),
                id_player_1=p1,
                id_player_2=p2,
                player_1_wins=p1_wins,
                player_2_wins=p2_wins,
                text_result=m.get("ResultString", ""),
                table_number=m.get("TableNumber"),
                is_feature_match=m.get("FeatureMatch", 0),
            ))
        return results

    @classmethod
    def insert_all(cls, connection, matches) -> None:
        connection.executemany(
            """
            INSERT OR IGNORE INTO match (id, id_round, id_player_1, id_player_2, player_1_wins, player_2_wins, text_result, table_number, is_feature_match)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (mt.id, mt.id_round, mt.id_player_1, mt.id_player_2, mt.player_1_wins, mt.player_2_wins, mt.text_result, mt.table_number, mt.is_feature_match)
                for mt in matches
            ],
        )
        connection.commit()
