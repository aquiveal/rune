from pathlib import Path

import requests
import vcr

CASSETTE_PATH = str(Path(__file__).parent / "cassettes" / "test_git_repository.yaml")


@vcr.use_cassette(CASSETTE_PATH)
def test_github_api_fetch():
    """Verify that vcrpy successfully mocks external HTTP interactions."""
    response = requests.get("https://api.github.com/repos/aquiveal/rune")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "rune"
