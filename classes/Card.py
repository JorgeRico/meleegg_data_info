class Card:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    @classmethod
    def from_decklist_records(cls, decklist_records: list) -> dict:
        """Extract unique cards from decklist detail records."""
        cards = {}
        for rec in decklist_records:
            name = rec.get("n", "")
            if name and name not in cards:
                cards[name] = cls(id=None, name=name)
        return cards

    @classmethod
    def insert_all(cls, connection, cards) -> dict:
        """Insert cards and return a mapping of name -> assigned id."""
        name_to_id = {}
        for name, card in cards.items():
            cursor = connection.execute(
                "INSERT OR IGNORE INTO card (name) VALUES (?)",
                (name,),
            )
            if cursor.lastrowid:
                name_to_id[name] = cursor.lastrowid
            else:
                row = connection.execute(
                    "SELECT id FROM card WHERE name = ?", (name,)
                ).fetchone()
                name_to_id[name] = row[0] if row else None
        connection.commit()
        return name_to_id
