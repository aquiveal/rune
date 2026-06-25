---
name: lume-python
description: Provides specialized context, rules, and tools for implementing, configuring, and debugging lume-python. Use this skill whenever modifying lume-python configurations or adding related functionality.
---
# lume-python

## File Tree

```text
lume-python/
├── assets
├── modules
│   └── lume-python (See AST Map below)
├── references
├── scripts
└── SKILL.md
```

> **Agent Instructions:** The AST maps below provide a high-level overview of the `modules/` directory. Note that the complete repository source code is available within the `modules/` folder. You can and should use your file reading tools to access the actual source code within `modules/` for complete details, implementation logic, and context beyond what the AST map provides.

### AST Map: `modules/lume-python`

```python
.agents\rules\architecture-application.md

.agents\rules\architecture-business.md

.agents\rules\architecture-data.md

.agents\rules\architecture-integration.md

.agents\rules\architecture-technology.md

.agents\rules\language-python\anti-patterns.md

.agents\rules\language-python\architecture-and-structure.md

.agents\rules\language-python\code-style-and-formatting.md

.agents\rules\language-python\configuration-and-environment.md

.agents\rules\language-python\dependency-management.md

.agents\rules\language-python\documentation-and-comments.md

.agents\rules\language-python\error-handling.md

.agents\rules\language-python\logging-and-observability.md

.agents\rules\language-python\naming-conventions.md

.agents\rules\language-python\performance-and-optimization.md

.agents\rules\language-python\security-and-validation.md

.agents\rules\language-python\testing-standards.md

.agents\rules\language-python\type-safety.md

.agents\skills\langfuse-python\SKILL.md

.agents\skills\posthog\SKILL.md

.agents\skills\sentry\SKILL.md

.agents\skills\windmill\SKILL.md

.github\pull_request_template.md

.github\workflows\release.yaml

.gitignore

.roo\rules\architecture-and-structure.md

.roo\rules\architecture-application.md

.roo\rules\architecture-business.md

.roo\rules\architecture-data.md

.roo\rules\architecture-integration.md

.roo\rules\architecture-technology.md

.roo\rules\language-python\anti-patterns.md

.roo\rules\language-python\architecture-and-structure.md

.roo\rules\language-python\code-style-and-formatting.md

.roo\rules\language-python\configuration-and-environment.md

.roo\rules\language-python\dependency-management.md

.roo\rules\language-python\documentation-and-comments.md

.roo\rules\language-python\error-handling.md

.roo\rules\language-python\logging-and-observability.md

.roo\rules\language-python\naming-conventions.md

.roo\rules\language-python\performance-and-optimization.md

.roo\rules\language-python\security-and-validation.md

.roo\rules\language-python\testing-standards.md

.roo\rules\language-python\type-safety.md

.rune\config

.rune\index

.runemodules

AGENTS.md

CHANGELOG.md

LICENSE

README.md

pdm.lock

pyproject.toml

src\lume\__init__.py

src\lume\config.py:
⋮
│def generate_traceparent() -> str:
⋮
│def resolve_traceparent() -> str:
⋮
│class LoggingSettings(BaseSettings):
│    """Configuration for the lume package."""
│
⋮
│    @computed_field  # type: ignore
│    @property
│    def is_windmill_env(self) -> bool:
⋮
│    @computed_field  # type: ignore
│    @property
│    def trace_id(self) -> str:
⋮
│    @computed_field  # type: ignore
│    @property
│    def span_id(self) -> str:
⋮

src\lume\integrations\__init__.py

src\lume\integrations\langfuse\__init__.py

src\lume\integrations\posthog\__init__.py

src\lume\integrations\sentry\__init__.py

src\lume\integrations\windmill.py:
⋮
│def get_windmill_traceparent() -> Optional[str]:
⋮

src\lume\logging.py:
⋮
│def setup_logging(settings: Optional[LoggingSettings] = None) -> None:
⋮

src\lume\service.py:
⋮
│def remove_otel_context(
│    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
⋮
│def rich_renderer(
│    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
⋮
│def get_console_format() -> Tuple[List[Any], List[logging.Handler]]:
⋮
│def add_otel_context(
│    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
⋮
│def setup_otel_provider(
│    settings_override: Optional[Any] = None,
⋮

tests\conftest.py:
⋮
│@pytest.fixture(autouse=True)
│def clean_structlog():
⋮
│@pytest.fixture(autouse=True)
│def env_reset():
⋮
│@pytest.fixture
│def in_memory_otel_exporters():
⋮

tests\integration\test_telemetry_integration.py:
⋮
│@mock.patch.dict(
│    os.environ,
│    {
│        "SENTRY_DSN": "https://dummy@sentry.io/123",
│        "POSTHOG_API_KEY": "ph_dummy_key",
│        "LANGFUSE_PUBLIC_KEY": "lf_pub",
│        "LANGFUSE_SECRET_KEY": "lf_sec",
│        "WM_TOKEN": "wm_dummy_token",
│        "WM_WORKSPACE": "wm_ws",
│        "WM_BASE_URL": "https://app.windmill.dev",
⋮
│def test_telemetry_integration(
│    mock_langfuse, mock_posthog, mock_sentry, in_memory_otel_exporters
│):
│    """
│    Integration test utilizing InMemory OpenTelemetry Exporters to verify
│    the fully configured pipeline accurately translates custom structured
│    logging events into W3C compliant OpenTelemetry LogRecords and spans.
⋮
│    @observe(as_type="generation")
│    def my_generation_func():
⋮

tests\performance\test_logging_concurrency.py:
⋮
│def test_thread_safe_contextvars():
│    """
│    Test that bound contextvars in structlog do not bleed across threads
│    under concurrent load.
⋮
│    with mock.patch("sys.stdout", out):
│        setup_logging(settings)
⋮
│        def worker(thread_idx: int):
⋮

tests\property\test_logging_properties.py:
⋮
│@given(
│    st.dictionaries(
│        st.text(), st.text() | st.integers() | st.none() | st.floats(allow_nan=False)
│    )
│)
│def test_remove_otel_context_never_crashes(event_dict):
⋮
│@mock.patch("lume.service.settings")
⋮
│def test_add_otel_context_never_crashes(mock_settings, event_dict):
⋮

tests\unit\lume\integrations\test_langfuse.py:
│def test_langfuse_facade_re_exported() -> None:
⋮

tests\unit\lume\integrations\test_posthog.py:
│def test_posthog_facade_re_exported() -> None:
⋮

tests\unit\lume\integrations\test_sentry.py:
│def test_sentry_facade_re_exported() -> None:
⋮

tests\unit\lume\integrations\test_windmill.py:
⋮
│@mock.patch.dict(
│    os.environ,
│    {"WM_TRACEPARENT": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"},
│    clear=True,
│)
│def test_get_windmill_traceparent_valid():
⋮
│@mock.patch.dict(os.environ, {}, clear=True)
│def test_get_windmill_traceparent_missing():
⋮
│def test_windmill_facade_re_exported() -> None:
⋮

tests\unit\lume\test_config.py:
⋮
│def test_default_settings():
⋮
│@mock.patch.dict(
│    os.environ,
│    {
│        "LOG_LEVEL": "DEBUG",
│        "STDOUT_FORMAT": "rich",
│        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
│        "TRACEPARENT": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
│    },
│    clear=True,
│)
│def test_settings_from_env():
⋮
│@mock.patch.dict(
│    os.environ,
│    {
│        "WM_TRACEPARENT": "00-windmilltraceid1234567890123456-windmillspanid12-01",
│    },
│    clear=True,
│)
│def test_settings_from_windmill_env():
⋮
│@mock.patch.dict(
│    os.environ,
│    {
│        "TRACEPARENT": "00-envtraceid1234567890123456789012-envspanid1234567-01",
│        "WM_TRACEPARENT": "00-windmilltraceid1234567890123456-windmillspanid12-01",
│    },
│    clear=True,
│)
│def test_settings_precedence_env_over_windmill():
⋮
│def test_is_windmill_env():
⋮
│def test_vendor_defaults():
⋮
│def test_generate_traceparent():
⋮
│def test_malformed_traceparent_fails():
⋮

tests\unit\lume\test_logging.py:
⋮
│@mock.patch("lume.logging.structlog.configure", spec=True)
│@mock.patch("lume.logging.setup_otel_provider", spec=True)
│def test_setup_logging(mock_setup_otel, mock_configure):
⋮
│@mock.patch("lume.logging.structlog.configure", spec=True)
│@mock.patch("lume.logging.setup_otel_provider", spec=True)
│def test_setup_logging_with_otel(mock_setup_otel, mock_configure):
⋮
│@mock.patch("lume.logging.structlog.configure", spec=True)
⋮
│def test_setup_logging_initializes_vendors(
│    mock_langfuse, mock_posthog, mock_sentry, mock_setup_otel, mock_configure
⋮
│@mock.patch("lume.logging.structlog.configure", spec=True)
⋮
│def test_setup_logging_zero_config(
│    mock_langfuse, mock_posthog, mock_sentry, mock_setup_otel, mock_configure
⋮
│def test_console_output_is_clean():
⋮
│def test_setup_logging_idempotency():
⋮

tests\unit\lume\test_service.py:
⋮
│def test_add_otel_context_with_active_span():
⋮
│@mock.patch("lume.service.settings")
│def test_add_otel_context_fallback_to_settings(mock_settings):
⋮
│@mock.patch("lume.service.settings")
│def test_add_otel_context_empty_event_dict(mock_settings):
⋮
│@mock.patch("lume.service.settings")
│def test_setup_otel_provider_no_endpoint(mock_settings):
⋮
│@mock.patch("lume.service.settings")
│def test_setup_otel_provider_with_endpoint(mock_settings):
⋮
│def test_remove_otel_context():
⋮
│def test_remove_otel_context_missing_keys():
⋮
```