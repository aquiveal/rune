from rune.schemas.rule_schema import Page, RuleSchema, Site


def test_rule_schema_defaults():
    schema = RuleSchema(name="my-rule", description="A rule description")
    assert schema.name == "my-rule"
    assert schema.description == "A rule description"
    assert schema.metadata is not None
    assert schema.metadata.internal is False
    assert schema.path is None


def test_page_schema():
    page = Page(
        title="Getting Started",
        url="https://example.com/docs/start",
        description="Introduction and setup guide",
        section="Quickstart",
    )
    assert page.title == "Getting Started"
    assert page.url == "https://example.com/docs/start"
    assert page.description == "Introduction and setup guide"
    assert page.section == "Quickstart"


def test_site_schema():
    site = Site(
        name="amazon-sp-api",
        title="Amazon SP-API",
        source_url="https://developer-docs.amazon/sp-api",
        description="Amazon Selling Partner API documentation",
        pages=[
            Page(
                title="API References",
                url="https://developer-docs.amazon/sp-api/reference",
                description="API endpoints and models",
            )
        ],
        crawl_instructions="Use crawl4ai md tool",
    )
    assert site.name == "amazon-sp-api"
    assert site.title == "Amazon SP-API"
    assert len(site.pages) == 1
    assert site.pages[0].title == "API References"
