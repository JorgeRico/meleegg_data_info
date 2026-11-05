class Deck:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    @classmethod
    def from_standings_data(cls, standings: list) -> dict:
        """Extract unique decks from standings Decklists."""
        decks = {}
        for standing in standings:
            for dl in standing.get("Decklists", []) or []:
                deck_id = dl.get("DecklistId")
                if deck_id and deck_id not in decks:
                    decks[deck_id] = cls(id=deck_id, name=dl.get("DecklistName", ""))
        return decks

    @classmethod
    def insert_all(cls, connection, decks) -> None:
        connection.executemany(
            "INSERT OR IGNORE INTO deck (id, name) VALUES (?, ?)",
            [(d.id, d.name) for d in decks.values()],
        )
        connection.commit()
