import vcr
import requests


@vcr.use_cassette("tests/integration/external/cassettes/github_api.yaml")
def test_github_api_fetch():
    """Verify that vcrpy successfully mocks external HTTP interactions."""
    response = requests.get("https://api.github.com/repos/aquiveal/rune")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "rune"
