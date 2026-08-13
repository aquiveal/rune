import json
from unittest.mock import MagicMock, patch

from rune.schemas.rule_schema import Page, Site
from rune.services import rule_service


def test_extract_seo_excerpt_dict():
    metadata = {
        "og:description": "OpenGraph description for SEO",
        "description": "Fallback meta description",
    }
    excerpt = rule_service.extract_seo_excerpt(metadata)
    assert excerpt == "OpenGraph description for SEO"

    empty_meta = {}
    assert rule_service.extract_seo_excerpt(empty_meta) is None


def test_extract_seo_excerpt_html():
    html_content = """
    <html>
        <head>
            <meta name="description" content="Official documentation for Selling Partner API." />
            <title>Amazon Developer Docs</title>
        </head>
        <body><h1>Welcome</h1></body>
    </html>
    """
    excerpt = rule_service.extract_seo_excerpt(html_content)
    assert excerpt == "Official documentation for Selling Partner API."


def test_parse_llms_txt():
    llms_content = """# Amazon Selling Partner API
> Comprehensive documentation index for developers

## API Reference
- [Orders API](https://developer-docs.amazon/sp-api/orders): Endpoints for fetching seller orders
- [Reports API](https://developer-docs.amazon/sp-api/reports): Scheduled report generation
"""
    site = rule_service.parse_llms_txt(
        llms_content,
        source_url="https://developer-docs.amazon/sp-api",
        default_name="amazon-sp-api",
    )
    assert site.name == "amazon-sp-api"
    assert site.title == "Amazon Selling Partner API"
    assert site.description == "Comprehensive documentation index for developers"
    assert len(site.pages) == 2
    assert site.pages[0].title == "Orders API"
    assert site.pages[0].url == "https://developer-docs.amazon/sp-api/orders"
    assert site.pages[0].description == "Endpoints for fetching seller orders"
    assert site.pages[0].section == "API Reference"


def test_extract_html_documentation_site():
    html_text = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>FastAPI Framework</title>
            <meta name="description" content="FastAPI high performance framework" />
        </head>
        <body>
            <h1>FastAPI</h1>
            <a href="/tutorial/first-steps" title="Step by step tutorial">First Steps</a>
            <a href="/advanced/custom-response">Custom Response</a>
            <a href="https://external-website.com/other">External Site</a>
            <a href="/image.png">Logo</a>
        </body>
    </html>
    """
    site = rule_service.extract_html_documentation_site(
        base_url="https://fastapi.tiangolo.com",
        html_content=html_text,
        default_name="fastapi",
    )
    assert site.name == "fastapi"
    assert site.title == "FastAPI Framework"
    assert site.description == "FastAPI high performance framework"
    assert len(site.pages) == 2
    assert site.pages[0].title == "First Steps"
    assert site.pages[0].url == "https://fastapi.tiangolo.com/tutorial/first-steps"
    assert site.pages[0].description == "Step by step tutorial"
    assert site.pages[1].title == "Custom Response"
    assert site.pages[1].url == "https://fastapi.tiangolo.com/advanced/custom-response"


def test_generate_site_rule_markdown():
    site = Site(
        name="amazon-sp-api",
        title="Amazon SP-API",
        source_url="https://developer-docs.amazon/sp-api",
        description="Official reference index",
        pages=[
            Page(
                title="Orders",
                url="https://developer-docs.amazon/sp-api/orders",
                description="Orders endpoints",
                section="Core",
            )
        ],
    )
    md = rule_service.generate_site_rule_markdown(site)
    assert "name: amazon-sp-api" in md
    assert "type: documentation" in md
    assert "# Amazon SP-API - Documentation & Live Crawl Index" in md
    assert "crawl4ai" in md
    assert "### Core" in md
    assert "- [Orders](https://developer-docs.amazon/sp-api/orders): Orders endpoints" in md


@patch("rune.services.rule_service.urllib.request.urlopen")
def test_crawl_with_crawl4ai_success(mock_urlopen):
    crawl_response = {
        "results": [
            {
                "metadata": {
                    "title": "Amazon SP-API Docs",
                    "description": "Live developer reference for selling partners",
                },
                "links": {
                    "internal": [
                        {
                            "href": "/sp-api/reference/orders",
                            "text": "Orders API Reference",
                            "description": "Manage orders",
                        }
                    ]
                },
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(crawl_response).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    site = rule_service.crawl_with_crawl4ai(
        "https://developer-docs.amazon/sp-api/reference"
    )
    assert site is not None
    assert site.title == "Amazon SP-API Docs"
    assert site.description == "Live developer reference for selling partners"
    assert len(site.pages) == 1
    assert (
        site.pages[0].url == "https://developer-docs.amazon/sp-api/reference/orders"
    )


def test_merge_rules_to_agents_md_creates_new_file(tmp_path):
    # Arrange
    repo_path = tmp_path
    rules_dir = repo_path / ".roo" / "rules" / "language-python"
    rules_dir.mkdir(parents=True)

    (rules_dir / "anti-patterns.md").write_text("# Anti-Patterns\n\nContent here.")

    # Act
    rule_service.merge_rules_to_agents_md(repo_path)

    # Assert
    agents_md = repo_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text()

    assert "# Rules" in content
    assert "## language-python" in content
    assert "### Anti-Patterns" in content
    assert "Content here." in content


def test_merge_rules_to_agents_md_updates_existing_block(tmp_path):
    # Arrange
    repo_path = tmp_path
    agents_md = repo_path / "AGENTS.md"
    agents_md.write_text(
        "Some header\n\n# Rules\n\nOld content\n\n# Another Section\n\nMore content"
    )

    rules_dir = repo_path / ".roo" / "rules" / "language-python"
    rules_dir.mkdir(parents=True)
    (rules_dir / "anti-patterns.md").write_text("# Anti-Patterns\n\nContent here.")

    # Act
    rule_service.merge_rules_to_agents_md(repo_path)

    # Assert
    content = agents_md.read_text()
    assert "Some header" in content
    assert "# Rules" in content
    assert "## language-python" in content
    assert "### Anti-Patterns" in content
    assert "Old content" not in content
    assert "# Another Section" in content
    assert "More content" in content


def test_merge_rules_to_agents_md_handles_unclosed_code_blocks(tmp_path):
    # Arrange
    repo_path = tmp_path
    rules_dir = repo_path / ".roo" / "rules" / "language-python"
    rules_dir.mkdir(parents=True)

    (rules_dir / "anti-patterns.md").write_text("```python\ndef foo():\n    pass\n")
    (rules_dir / "other.md").write_text("Other content")

    # Act
    rule_service.merge_rules_to_agents_md(repo_path)

    # Assert
    agents_md = repo_path / "AGENTS.md"
    content = agents_md.read_text()

    # The unclosed code block should be closed before the next file
    assert "```python\ndef foo():\n    pass\n```" in content
    assert "Other content" in content


def test_merge_rules_to_agents_md_finds_standalone_files(tmp_path):
    # Arrange
    repo_path = tmp_path
    rules_dir = repo_path / ".roo" / "rules"
    rules_dir.mkdir(parents=True)

    (rules_dir / "my-rule.md").write_text("# My Rule\n\nContent here.")

    # Act
    rule_service.merge_rules_to_agents_md(repo_path)

    # Assert
    agents_md = repo_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text()

    assert "# Rules" in content
    assert "## my-rule" not in content
    assert "## My Rule" in content
    assert "Content here." in content


def test_merge_rules_to_agents_md_ignores_empty_files(tmp_path):
    # Arrange
    repo_path = tmp_path
    rules_dir = repo_path / ".roo" / "rules"
    rules_dir.mkdir(parents=True)

    (rules_dir / "empty-rule.md").write_text("")
    (rules_dir / "whitespace-rule.md").write_text("   \n  \t  ")
    (rules_dir / "valid-rule.md").write_text("# Valid Rule\n\nContent here.")

    # Act
    rule_service.merge_rules_to_agents_md(repo_path)

    # Assert
    agents_md = repo_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text()

    assert "## empty-rule" not in content
    assert "## whitespace-rule" not in content
    assert "## valid-rule" not in content
    assert "## Valid Rule" in content
