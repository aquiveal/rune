import html.parser
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import structlog
import yaml

from rune.config.exceptions import ValidationError
from rune.config.main import settings
from rune.repositories import module_repository
from rune.schemas.module_schema import ModuleSchema
from rune.schemas.rule_schema import Page, RuleSchema, Site
from rune.services import mcp_service
from rune.utils.url import resolve_relative_url, slugify_url

__all__ = [
    "crawl_with_crawl4ai",
    "create_rule_from_doc_url",
    "discover_rule_dirs",
    "discover_rules",
    "extract_html_documentation_site",
    "extract_seo_excerpt",
    "generate_site_rule_markdown",
    "merge_rules_to_agents_md",
    "parse_llms_txt",
    "validate_rule_file",
]

logger = structlog.get_logger(__name__)


class _DocHTMLParser(html.parser.HTMLParser):
    """HTML Parser for extracting title, SEO meta tags, and internal doc links."""

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.title = ""
        self.meta_description = ""
        self.og_description = ""
        self.twitter_description = ""
        self.h1_title = ""
        self.pages: list[Page] = []
        self._seen_urls: set[str] = set()

        self._in_title = False
        self._in_h1 = False
        self._current_a_href: str | None = None
        self._current_a_title: str | None = None
        self._current_a_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attr_dict = {k.lower(): v for k, v in attrs if v is not None}

        if tag == "title":
            self._in_title = True
        elif tag == "h1" and not self.h1_title:
            self._in_h1 = True
        elif tag == "meta":
            name = attr_dict.get("name", "").lower()
            prop = attr_dict.get("property", "").lower()
            content = attr_dict.get("content", "").strip()

            if name == "description" and not self.meta_description:
                self.meta_description = content
            elif (
                prop in ["og:description", "twitter:description"]
                and not self.og_description
            ):
                self.og_description = content
            elif name == "twitter:description" and not self.twitter_description:
                self.twitter_description = content
        elif tag == "a":
            href = attr_dict.get("href")
            if href:
                self._current_a_href = href
                self._current_a_title = attr_dict.get("title")
                self._current_a_text = []

    def handle_endtag(self, tag: str):
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
        elif tag == "a" and self._current_a_href:
            link_text = " ".join(self._current_a_text).strip()
            raw_href = self._current_a_href
            self._current_a_href = None
            self._current_a_text = []

            # Ignore non-http links or fragment-only jumps
            if (
                raw_href.startswith(("#", "mailto:", "javascript:", "tel:"))
                or not raw_href
            ):
                return

            full_url = resolve_relative_url(self.base_url, raw_href)

            # Filter asset extensions
            parsed_url = urllib.parse.urlparse(full_url)
            path_lower = parsed_url.path.lower()
            if any(
                path_lower.endswith(ext)
                for ext in [
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".svg",
                    ".css",
                    ".js",
                    ".ico",
                    ".zip",
                    ".tar.gz",
                    ".pdf",
                ]
            ):
                return

            # Keep only links on the same domain or path hierarchy
            base_parsed = urllib.parse.urlparse(self.base_url)
            if parsed_url.netloc and parsed_url.netloc != base_parsed.netloc:
                return

            if full_url in self._seen_urls:
                return
            self._seen_urls.add(full_url)

            title = (
                link_text
                or self._current_a_title
                or slugify_url(full_url).replace("-", " ").title()
            )
            desc = self._current_a_title if self._current_a_title else None
            self.pages.append(Page(title=title, url=full_url, description=desc))

    def handle_data(self, data: str):
        cleaned = data.strip()
        if not cleaned:
            return
        if self._in_title:
            self.title += f" {cleaned}"
        elif self._in_h1:
            self.h1_title += f" {cleaned}"
        elif self._current_a_href:
            self._current_a_text.append(cleaned)


def extract_seo_excerpt(html_or_metadata: dict[str, Any] | str) -> str | None:
    """Extract an SEO excerpt from Crawl4AI metadata dict or HTML content."""
    if isinstance(html_or_metadata, dict):
        for key in [
            "og:description",
            "description",
            "twitter:description",
            "excerpt",
            "summary",
        ]:
            val = html_or_metadata.get(key)
            if val and isinstance(val, str) and val.strip():
                return val.strip()[:250]
        return None

    # HTML string extraction
    parser = _DocHTMLParser(base_url="")
    parser.feed(html_or_metadata)
    desc = (
        parser.meta_description
        or parser.og_description
        or parser.twitter_description
    )
    return desc.strip()[:250] if desc else None


def crawl_with_crawl4ai(
    url: str,
    base_url: str = "http://localhost:11235",
    api_token: str = "crawl4ai-token",
    timeout: int = 30,
) -> Site | None:
    """Crawl a documentation URL via the Crawl4AI REST API."""
    endpoint = f"{base_url.rstrip('/')}/crawl"
    payload = {
        "urls": url,
        "priority": 10,
        "word_count_threshold": 10,
        "extraction_strategy": "NoExtractionStrategy",
    }
    data_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                return None
            res_data = json.loads(response.read().decode("utf-8"))

        # Crawl4AI response structure may return a list or dict
        result_item = (
            res_data[0]
            if isinstance(res_data, list) and res_data
            else (
                res_data.get("results", [{}])[0]
                if isinstance(res_data, dict) and "results" in res_data
                else res_data
            )
        )

        metadata = result_item.get("metadata", {})
        title = (
            metadata.get("title")
            or metadata.get("og:title")
            or slugify_url(url).replace("-", " ").title()
        )
        description = extract_seo_excerpt(metadata) or ""

        # Extract internal links from Crawl4AI payload
        links_data = result_item.get("links", {})
        internal_links = links_data.get("internal", [])

        pages: list[Page] = []
        seen = {url}

        base_parsed = urllib.parse.urlparse(url)

        for link_obj in internal_links:
            href = (
                link_obj.get("href")
                if isinstance(link_obj, dict)
                else str(link_obj)
            )
            if not href or href.startswith(
                ("#", "mailto:", "javascript:", "tel:")
            ):
                continue
            full_url = resolve_relative_url(url, href)
            parsed_link = urllib.parse.urlparse(full_url)
            if parsed_link.netloc and parsed_link.netloc != base_parsed.netloc:
                continue
            if full_url in seen:
                continue
            seen.add(full_url)

            text = (
                link_obj.get("text") or link_obj.get("title")
                if isinstance(link_obj, dict)
                else ""
            )
            link_title = (
                text.strip()
                if text
                else slugify_url(full_url).replace("-", " ").title()
            )
            link_desc = (
                link_obj.get("description")
                if isinstance(link_obj, dict)
                else None
            )
            pages.append(
                Page(title=link_title, url=full_url, description=link_desc)
            )

        name = slugify_url(url)
        return Site(
            name=name,
            title=title.strip(),
            source_url=url,
            description=description,
            pages=pages,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(
            f"Crawl4AI container request failed, falling back to standard parser: {e}"
        )
        return None


def extract_html_documentation_site(
    base_url: str, html_content: str, default_name: str = ""
) -> Site:
    """Parse raw HTML content to construct a documentation Site and Pages index."""
    parser = _DocHTMLParser(base_url=base_url)
    parser.feed(html_content)

    title = (
        parser.title.strip()
        or parser.h1_title.strip()
        or slugify_url(base_url).replace("-", " ").title()
    )
    description = (
        parser.meta_description
        or parser.og_description
        or parser.twitter_description
        or ""
    ).strip()

    name = default_name or slugify_url(base_url)
    return Site(
        name=name,
        title=title,
        source_url=base_url,
        description=description,
        pages=parser.pages,
    )


def parse_llms_txt(
    llms_txt_content: str, source_url: str, default_name: str = ""
) -> Site:
    """Parse standard llms.txt format into a Site and Pages schema."""
    lines = llms_txt_content.splitlines()
    title = ""
    description_lines = []
    pages: list[Page] = []
    current_section = None

    link_regex = re.compile(
        r"^-\s*\[(?P<title>[^\]]+)\]\((?P<url>[^\)]+)\)(?::\s*(?P<desc>.*))?$"
    )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
        elif stripped.startswith("## "):
            current_section = stripped[3:].strip()
        elif stripped.startswith("> "):
            description_lines.append(stripped[2:].strip())
        elif stripped.startswith("- ["):
            match = link_regex.match(stripped)
            if match:
                l_title = match.group("title").strip()
                l_url = resolve_relative_url(
                    source_url, match.group("url").strip()
                )
                l_desc = (
                    match.group("desc").strip()
                    if match.group("desc")
                    else None
                )
                pages.append(
                    Page(
                        title=l_title,
                        url=l_url,
                        description=l_desc,
                        section=current_section,
                    )
                )
        elif not title and not pages and not stripped.startswith("-"):
            description_lines.append(stripped)

    name = default_name or slugify_url(source_url)
    return Site(
        name=name,
        title=title or name.replace("-", " ").title(),
        source_url=source_url,
        description=" ".join(description_lines).strip(),
        pages=pages,
    )


def generate_site_rule_markdown(site: Site) -> str:
    """Generate llms.txt compliant markdown rule content with Crawl4AI live directives."""
    frontmatter = {
        "name": site.name,
        "description": site.description
        or f"Documentation live index and Crawl4AI crawl directives for {site.title}",
        "source": site.source_url,
        "type": "documentation",
    }

    yaml_header = yaml.safe_dump(frontmatter, sort_keys=False).strip()

    md = f"---\n{yaml_header}\n---\n\n"
    md += f"# {site.title} - Documentation & Live Crawl Index\n\n"
    if site.description:
        md += f"> {site.description}\n\n"

    md += "## 🎯 Agent Instructions & Dynamic Crawling Directives\n\n"
    md += (
        f"- When answering questions, checking models, or implementing features for `{site.title}`, "
        "DO NOT guess endpoints, parameters, or specifications.\n"
        "- Use the `crawl4ai` MCP server (tools: `crawl`, `md`, or `read_url`) to dynamically fetch, "
        "scrape, and read documentation pages on-demand for accurate, up-to-date API references.\n"
        f"- Root Documentation URL: {site.source_url}\n\n"
    )

    md += "## 📚 Documentation Index (llms.txt)\n\n"
    if site.pages:
        current_section = None
        for p in site.pages:
            if p.section and p.section != current_section:
                current_section = p.section
                md += f"### {current_section}\n\n"
            desc_part = f": {p.description}" if p.description else ""
            md += f"- [{p.title}]({p.url}){desc_part}\n"
        md += "\n"
    else:
        md += f"- [{site.title}]({site.source_url})\n\n"

    return md


def create_rule_from_doc_url(
    url: str,
    name: str | None,
    git_root: Path,
    cwd: Path,
    target_agents: list[str],
    global_scope: bool = False,
) -> Path:
    """Orchestrate documentation scraping via Crawl4AI, generate rule files, and merge to AGENTS.md."""
    base_dir = (Path.home() / ".rune") if global_scope else git_root
    rule_name = name or slugify_url(url)

    # 1. Ensure Crawl4AI Docker container is running if Docker is present
    mcp_service.ensure_crawl4ai_docker_container()

    site = None

    # 2. Check for llms.txt first
    parsed_base = urllib.parse.urlparse(url)
    domain_root = f"{parsed_base.scheme}://{parsed_base.netloc}"
    probed_urls = [
        f"{url.rstrip('/')}/llms.txt",
        f"{domain_root}/llms.txt",
        f"{url.rstrip('/')}/llms-full.txt",
        f"{domain_root}/llms-full.txt",
    ]

    for p_url in probed_urls:
        try:
            req = urllib.request.Request(
                p_url,
                headers={
                    "User-Agent": "Rune-Doc-Crawler/1.0 (LLM Rules Indexer)"
                },
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    content = response.read().decode("utf-8")
                    if content and "# " in content:
                        site = parse_llms_txt(
                            content, source_url=url, default_name=rule_name
                        )
                        break
        except Exception:  # noqa: BLE001, S110
            pass

    # 3. If llms.txt not found, attempt Crawl4AI crawl
    if site is None:
        site = crawl_with_crawl4ai(url)

    # 4. Fallback to standard HTTP fetch and HTML parser
    if site is None or not site.pages:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Rune-Doc-Crawler/1.0 (LLM Rules Indexer)"
                },
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                html_text = response.read().decode("utf-8", errors="ignore")
                site = extract_html_documentation_site(
                    url, html_text, default_name=rule_name
                )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"Direct fetch of {url} encountered an error: {e}. Generating baseline rule."
            )
            site = Site(
                name=rule_name,
                title=rule_name.replace("-", " ").title(),
                source_url=url,
                description=f"Documentation reference for {url}",
                pages=[
                    Page(
                        title=rule_name.replace("-", " ").title(),
                        url=url,
                        description="Main documentation entrypoint",
                    )
                ],
            )

    site.name = rule_name
    rule_markdown = generate_site_rule_markdown(site)

    # 5. Write rule file to target agent directories
    target_rule_paths = []
    if target_agents:
        for agent in target_agents:
            target_rule_paths.append(base_dir / agent / "rules" / f"{rule_name}.md")
    else:
        if cwd.name == "rules":
            target_rule_paths.append(cwd / f"{rule_name}.md")
        else:
            target_rule_paths.append(cwd / "rules" / f"{rule_name}.md")

    for path in target_rule_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rule_markdown, encoding="utf-8")
        rel_path = str(path.relative_to(base_dir)).replace("\\", "/")
        try:
            module_repository.add_module(
                base_dir, ModuleSchema(name=rel_path, url=url, path=rel_path)
            )
        except Exception:  # noqa: BLE001, S110
            pass
        logger.info(f"Created documentation rule '{rule_name}' at {path}")

    # 6. Ensure crawl4ai MCP server is configured for target agents
    try:
        mcp_service.add_mcp_server(
            source="crawl4ai",
            git_root=git_root,
            cwd=cwd,
            global_scope=global_scope,
            agent_override=target_agents,
        )
    except Exception as e:  # noqa: BLE001
        logger.debug(f"Crawl4AI MCP server setup notification: {e}")

    # 7. Merge updated rules to AGENTS.md
    try:
        merge_rules_to_agents_md(git_root or cwd)
        logger.info("Successfully merged documentation rule into AGENTS.md")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to merge rules: {e}")

    return target_rule_paths[0] if target_rule_paths else (cwd / f"{rule_name}.md")


def validate_rule_file(path: Path) -> RuleSchema:
    # Rules might be .clinerules or RULE.md or similar
    # For now, let's assume they also use YAML frontmatter if they are RULE.md
    if not path.exists():
        raise ValidationError(f"Rule file not found at {path}")

    try:
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                if isinstance(frontmatter, dict):
                    return RuleSchema(**frontmatter)

        # Fallback for files without frontmatter (like .clinerules)
        return RuleSchema(name=path.name, description=f"Rule from {path.name}")
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Validation failed: {e}")


def discover_rules(repo_path: Path) -> list[RuleSchema]:
    rules = []
    # Search for .clinerules, .cursorrules, and RULE.md
    patterns = [".clinerules", ".cursorrules", "RULE.md", "rules/*.md"]

    found_files = []
    for pattern in patterns:
        found_files.extend(list(repo_path.glob(f"**/{pattern}")))

    seen_paths = set()
    for rule_file in found_files:
        abs_path = rule_file.absolute()
        if abs_path in seen_paths:
            continue
        seen_paths.add(abs_path)

        try:
            rule = validate_rule_file(rule_file)
            rule.path = str(rule_file.relative_to(repo_path)).replace("\\", "/")
            rules.append(rule)
        except ValidationError:
            continue

    # Also discover directories inside 'rules/'
    rules_dir = repo_path / "rules"
    if rules_dir.exists() and rules_dir.is_dir():
        for child in rules_dir.iterdir():
            if child.is_dir():
                abs_path = child.absolute()
                if abs_path not in seen_paths:
                    seen_paths.add(abs_path)
                    rule = RuleSchema(
                        name=child.name,
                        description=f"Rule directory {child.name}",
                        path=f"rules/{child.name}",
                    )
                    rules.append(rule)

    return rules


def discover_rule_dirs(repo_path: Path) -> list[Path]:
    rule_dirs = []
    rule_search_paths = settings.get_rule_search_paths()

    for rel_path in rule_search_paths:
        rules_dir = repo_path / Path(rel_path)
        if rules_dir.exists() and rules_dir.is_dir():
            # The rules can be subdirectories or standalone markdown files
            for child in rules_dir.iterdir():
                if child.is_dir() or (child.is_file() and child.suffix == ".md"):
                    rule_dirs.append(child)

    return rule_dirs


def merge_rules_to_agents_md(repo_path: Path):
    rule_dirs = discover_rule_dirs(repo_path)
    if not rule_dirs:
        return

    rules_block = "# Rules\n\n"

    for rule_item in rule_dirs:
        if rule_item.is_dir():
            md_files = sorted(rule_item.glob("*.md"))
            if not md_files:
                continue

            # Filter out empty files
            valid_files = []
            for md_file in md_files:
                content = md_file.read_text(encoding="utf-8").strip()
                if content:
                    valid_files.append((md_file, content))

            if not valid_files:
                continue

            rules_block += f"## {rule_item.name}\n\n"

            for md_file, content in valid_files:
                # Strip frontmatter if present
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()

                # Shift headings in the content by 2 levels to maintain hierarchy under ## {rule_item.name}
                content = re.sub(
                    r"^(#+)\s", r"##\1 ", content, flags=re.MULTILINE
                )

                # Handle unclosed code blocks
                code_block_count = len(
                    re.findall(r"^\s*```", content, flags=re.MULTILINE)
                )
                if code_block_count % 2 != 0:
                    content += "\n```"

                rules_block += f"{content}\n\n"
        elif rule_item.is_file() and rule_item.suffix == ".md":
            content = rule_item.read_text(encoding="utf-8").strip()
            if not content:
                continue

            # Strip frontmatter if present
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            # Shift headings in the content by 1 level to maintain hierarchy under # Rules
            content = re.sub(r"^(#+)\s", r"#\1 ", content, flags=re.MULTILINE)

            # Handle unclosed code blocks
            code_block_count = len(
                re.findall(r"^\s*```", content, flags=re.MULTILINE)
            )
            if code_block_count % 2 != 0:
                content += "\n```"

            rules_block += f"{content}\n\n"

    agents_md = repo_path / "AGENTS.md"

    if agents_md.exists():
        content = agents_md.read_text(encoding="utf-8")
        # Match from # Rules until the next # (h1) or end of file
        pattern = re.compile(r"# Rules\b.*?(?=\n# |\Z)", re.DOTALL)
        if pattern.search(content):
            new_content = pattern.sub(rules_block.strip(), content)
        else:
            # If no block found, append it
            new_content = (
                content.rstrip() + "\n\n" + rules_block.strip() + "\n"
            )
        agents_md.write_text(new_content, encoding="utf-8")
    else:
        agents_md.write_text(rules_block, encoding="utf-8")

