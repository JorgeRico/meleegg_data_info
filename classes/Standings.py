class Standings:
    def __init__(self, id: int, id_round: int, id_player_1: int, id_player_2: int, player_1_wins: int, player_2_wins: int, text_result: str):
        self.id = id
        self.id_round = id_round
        self.id_player_1 = id_player_1
        self.id_player_2 = id_player_2
        self.player_1_wins = player_1_wins
        self.player_2_wins = player_2_wins
        self.text_result = text_result
