class Decklist:
    def __init__(self, id: int, id_deck: str, id_card: int, total: int, is_sideboard: bool, is_maindeck: bool):
        self.id = id
        self.id_deck = id_deck
        self.id_card = id_card
        self.total = total
        self.is_sideboard = is_sideboard
        self.is_maindeck = is_maindeck

    @classmethod
    def from_decklist_details(cls, deck_id: str, details: dict, name_to_id: dict) -> list:
        """Convert decklist detail API response into Decklist objects."""
        decklists = []
        for rec in details.get("Records", []):
            card_name = rec.get("n", "")
            card_id = name_to_id.get(card_name)
            if card_id is None:
                continue
            quantity = rec.get("q", 0)
            c = rec.get("c", 0)
            is_sideboard = c == 99
            is_maindeck = c == 0
            decklists.append(cls(
                id=None,
                id_deck=deck_id,
                id_card=card_id,
                total=quantity,
                is_sideboard=is_sideboard,
                is_maindeck=is_maindeck,
            ))
        return decklists

    @classmethod
    def insert_all(cls, connection, decklists) -> None:
        connection.executemany(
            """
            INSERT OR IGNORE INTO decklist (id_deck, id_card, total, is_sideboard, is_maindeck)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (dl.id_deck, dl.id_card, dl.total, int(dl.is_sideboard), int(dl.is_maindeck))
                for dl in decklists
            ],
        )
        connection.commit()
