# Changelog v1.1.0

## Features

* **Lume-Python Integration**
  Replaced the deprecated `python-logging` implementation with `lume-python` and updated all associated dependencies to support the new logging architecture.
  Commits: [fb222fc](https://github.com/aquiveal/rune/commit/fb222fc0), [c88ce88](https://github.com/aquiveal/rune/commit/c88ce888), [a060904](https://github.com/aquiveal/rune/commit/a0609049)

* **Agent Skill Documentation**
  Introduced `SKILL.md` to provide agents with necessary context, operational rules, and an AST map for the `lume-python` package.
  Commit: [7d02ed4](https://github.com/aquiveal/rune/commit/7d02ed4d)

## Improvements

* **Dependency Updates**
  Updated core dependencies including OpenTelemetry, `posthog`, and `protobuf` to their latest stable versions.
  Commit: [a060904](https://github.com/aquiveal/rune/commit/a0609049)

* **Observability and Monitoring Additions**
  Integrated `langfuse` and `sentry-sdk` into the dependency stack to improve tracing and error reporting capabilities.
  Commit: [a060904](https://github.com/aquiveal/rune/commit/a0609049)

## Other

* **Documentation Cleanup**
  Removed legacy documentation files related to deprecated frameworks and SEO guides to reduce repository noise.
  Commit: [135d82e](https://github.com/aquiveal/rune/commit/135d82e7)
