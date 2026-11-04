class Decklist:
    def __init__(self, id: int, id_deck: int, id_card: int, total: int, is_sideboard: bool, is_maindeck: bool):
        self.id = id
        self.id_deck = id_deck
        self.id_card = id_card
        self.total = total
        self.is_sideboard = is_sideboard
        self.is_maindeck = is_maindeck
