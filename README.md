# Eternal Weekend Tournament Toolkit

A toolkit for crawling, processing, and exporting Magic: The Gathering tournament data from [melee.gg](https://melee.gg).

## Project Structure

```
eternal_weekend/
├── classes/
│   ├── __init__.py         # Package exports
│   ├── Card.py             # Card model with from_decklist_records() & insert_all()
│   ├── Deck.py             # Deck model with from_standings_data() & insert_all()
│   ├── Decklist.py         # Decklist model with from_decklist_details() & insert_all()
│   ├── Match.py            # Match model with from_match_data() & insert_all()
│   ├── Menu.py             # Interactive menu toolkit
│   ├── Player.py           # Player model with from_standings() & insert_all()
│   ├── Round.py            # Round model with from_dict() & insert_all()
│   ├── Standings.py        # Standings model with fetch_round_standings(), fetch_round_matches(), from_standings_data(), & insert_all()
│   ├── Tournament.py       # Tournament crawler & data orchestrator
│   └── db/
│       ├── __init__.py
│       └── db.py           # Db class (SQLite connection & schema)
├── helpers/
│   ├── __init__.py
│   └── excel.py            # ExcelHelper (Excel export utilities)
├── raw_data/               # Crawled JSON data
├── output_files/           # Exported Excel files
├── database/
│   └── eternal_weekend.db  # SQLite database
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Shared fixtures & sample data
│   ├── pytest.ini          # Test configuration
│   ├── test_classes/       # Unit tests for model classes
│   │   ├── test_card.py
│   │   ├── test_deck.py
│   │   ├── test_decklist.py
│   │   ├── test_match.py
│   │   ├── test_player.py
│   │   ├── test_round.py
│   │   ├── test_standings.py
│   │   └── test_tournament.py
│   ├── test_db/            # Database schema & insert tests
│   │   ├── test_db_schema.py
│   │   └── test_db_insert.py
│   ├── test_helpers/       # Helper utility tests
│   │   └── test_excel.py
│   └── test_integration/   # Integration tests
│       ├── test_menu.py    # Menu integration tests
│       └── test_pipeline.py
├── main.py                 # Application entry point
└── requirements.txt        # Python dependencies
```

## Database Tables

| Table        | Description                                  |
|--------------|----------------------------------------------|
| `deck`       | Decklist UUID → Deck name                    |
| `card`       | Card ID → Card name (unique)                 |
| `decklist`   | Deck-to-card mapping with quantities         |
| `round`      | Tournament round IDs and names               |
| `player`     | Player info with decklist reference          |
| `match`      | Match results with table number & flags      |
| `standings`  | Per-player per-round standings & points      |

### Table Schema Details

**deck**: `id` (TEXT PK), `name` (TEXT NOT NULL)
**card**: `id` (INTEGER PK AUTOINCREMENT), `name` (TEXT NOT NULL UNIQUE)
**decklist**: `id` (INTEGER PK), `id_deck` (TEXT NOT NULL), `id_card` (INTEGER NOT NULL), `total` (INTEGER NOT NULL), `is_sideboard` (INTEGER NOT NULL), `is_maindeck` (INTEGER NOT NULL)
**round**: `id` (INTEGER PK), `name` (TEXT NOT NULL)
**player**: `id` (INTEGER PK), `team_id` (INTEGER NOT NULL), `display_name` (TEXT NOT NULL), `username` (TEXT NOT NULL), `decklist_id` (TEXT)
**match**: `id` (TEXT PK), `id_round` (INTEGER NOT NULL), `id_player_1` (INTEGER NOT NULL), `id_player_2` (INTEGER NOT NULL), `player_1_wins` (INTEGER NOT NULL), `player_2_wins` (INTEGER NOT NULL), `text_result` (TEXT NOT NULL), `table_number` (INTEGER), `is_feature_match` (INTEGER NOT NULL DEFAULT 0)
**standings**: `id_player` (INTEGER NOT NULL PK), `id_round` (INTEGER NOT NULL PK), `match_record` (TEXT NOT NULL), `game_record` (TEXT NOT NULL), `points` (INTEGER NOT NULL)

## Testing

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures: sample data, temp DB, seeded Menu
├── pytest.ini               # Test configuration
├── test_classes/            # Unit tests for all model classes
│   ├── test_card.py         # Card: creation, from_decklist_records(), insert_all()
│   ├── test_deck.py         # Deck: creation, from_standings_data(), insert_all()
│   ├── test_decklist.py     # Decklist: creation, from_decklist_details(), insert_all()
│   ├── test_match.py        # Match: creation, from_match_data(), insert_all()
│   ├── test_player.py       # Player: creation, from_standings(), insert_all()
│   ├── test_round.py        # Round: creation, from_dict(), insert_all()
│   ├── test_standings.py    # Standings: creation, from_standings_data(), fetch_round_standings(), fetch_round_matches(), insert_all()
│   └── test_tournament.py   # Tournament: get_tournament_id(), _build_session(), fetch_tournament_data(), fetch_all_round_standings(), fetch_all_round_matches(), fetch_all_decklist_details(), save_to_database()
├── test_db/                 # Database schema & insert tests
│   ├── test_db_schema.py    # Table creation & column verification
│   └── test_db_insert.py    # Direct DB insert verification
├── test_helpers/            # Helper utility tests
│   └── test_excel.py        # ExcelHelper export tests
└── test_integration/        # Integration tests
    ├── test_menu.py         # Menu commands with seeded database
    └── test_pipeline.py     # Pipeline utility tests
```

### Running Tests

```bash
# Install test dependencies
pip install pytest openpyxl pytest-cov

# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_classes/test_card.py -v

# Run with coverage
python3 -m pytest tests/ --cov=classes --cov=helpers
```

### Test Coverage

- **Model classes**: Creation, `from_*` class methods, `insert_all` database insertion
- **Database schema**: All 7 tables created with correct columns (`match` includes `table_number` and `is_feature_match`)
- **Database inserts**: Idempotent `INSERT OR IGNORE` behavior
- **ExcelHelper**: Export with list rows, dict rows, directory creation, existing file cleanup
- **Menu integration**: `get_player_decklists()`, `get_maindeck_stats()`, `get_sideboard_stats()`, `get_standings()`, `get_tournament_info()` — all verified against a seeded in-memory SQLite database

## Usage

```bash
# Run the interactive menu
python3 main.py
```

### Menu Options

1. **Get Tournament Info** — Crawl melee.gg, fetch all rounds/standings/matches/decklists, save JSON + populate database
2. **Get Player Decklists** — Group players by decklist name, export to `output_files/decklists.xlsx`
3. **Get Decklist Stats** — (placeholder)
4. **Get Standings** — Export match results per round to `output_files/standings.xlsx` (one sheet per round, with player points)
5. **Get Maindeck Stats** — Group maindeck cards by name with totals, export to `output_files/maindeck_cards.xlsx`
6. **Get Sideboard Stats** — Group sideboard cards by name with totals, export to `output_files/sideboard_cards.xlsx`
7. **Exit** — Quit the application

## Class Reference

### Tournament
- `get_tournament_id(url)` — Extract tournament ID from URL
- `_build_session()` — Create requests session with proper headers
- `_extract_tournament_page(url)` — Render tournament page & extract rounds with BeautifulSoup
- `fetch_tournament_data(url, file_name)` — Orchestrate full tournament crawl: standings, matches, decklists, save JSON + database

### Standings
- `fetch_round_standings(session, round_id)` — Fetch standings for a round via DataTables pagination
- `fetch_round_matches(session, round_id)` — Fetch match data for a round via DataTables pagination
- `from_standings_data(standings_data)` — Convert API standings to Standings objects
- `insert_all(connection, standings)` — Bulk insert standings into database

### Round
- `from_dict(data)` — Create Round from API data
- `insert_all(connection, rounds)` — Bulk insert rounds into database

### Deck
- `from_standings_data(standings)` — Extract unique decks from standings
- `insert_all(connection, decks)` — Bulk insert decks into database

### Card
- `from_decklist_records(decklist_records)` — Extract unique cards from decklist details
- `insert_all(connection, cards)` — Bulk insert cards into database

### Decklist
- `from_decklist_details(deck_id, details, name_to_id)` — Convert decklist API response to Decklist objects
- `insert_all(connection, decklists)` — Bulk insert decklists into database

### Player
- `from_standings(standings)` — Extract unique players from standings
- `insert_all(connection, players)` — Bulk insert players into database

### Match
- `from_match_data(matches)` — Convert API match data to Match objects
- `insert_all(connection, matches)` — Bulk insert matches into database

### Db
- `get_connection()` — Create SQLite connection
- `drop_tables(connection)` — Drop all tables
- `create_tables(connection)` — Create all tables
- `init_database()` — Initialize database

### ExcelHelper
- `export_to_excel(data, headers, file_name, sheet_name, output_dir)` — Export data to Excel
- `prepare_output_file(file_name, output_dir)` — Create output directory and remove existing file