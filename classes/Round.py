class Round:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, data: dict) -> "Round":
        return cls(id=int(data["round_id"]), name=data["round_name"])

    @classmethod
    def insert_all(cls, connection, rounds) -> None:
        connection.executemany(
            "INSERT OR IGNORE INTO round (id, name) VALUES (?, ?)",
            [(r.id, r.name) for r in rounds],
        )
        connection.commit()
