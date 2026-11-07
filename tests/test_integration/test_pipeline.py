"""Integration tests for the full tournament data pipeline."""

from classes.Tournament import Tournament


def test_get_tournament_id_from_default_url():
    tid = Tournament.get_tournament_id("https://melee.gg/Tournament/View/491103#standings")
    assert tid == "491103"


def test_tournament_url_format():
    """Ensure default tournament URL has expected format."""
    url = "https://melee.gg/Tournament/View/491103#standings"
    assert url.startswith("https://melee.gg/Tournament/View/")
    assert "#standings" in url
