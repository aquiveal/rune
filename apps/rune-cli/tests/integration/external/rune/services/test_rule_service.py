from pathlib import Path

import requests
import vcr
from rune.services import rule_service

CASSETTE_PATH = str(Path(__file__).parent / "cassettes" / "test_rule_service.yaml")


@vcr.use_cassette(CASSETTE_PATH, record_mode="none")
def test_external_doc_crawl_llms_txt_fetch():
    """Verify fetching and parsing of public llms.txt endpoints."""
    response = requests.get(
        "https://fastapi.tiangolo.com/llms.txt",
        headers={"User-Agent": "python-requests/2.32.5"},
        timeout=10,
    )
    assert response.status_code == 200
    content = response.text

    site = rule_service.parse_llms_txt(
        content,
        source_url="https://fastapi.tiangolo.com",
        default_name="fastapi",
    )

    assert site.name == "fastapi"
    assert site.title == "FastAPI"
    assert len(site.pages) == 2
    assert site.pages[0].title == "Tutorial - User Guide"
    assert site.pages[0].url == "https://fastapi.tiangolo.com/tutorial/"
