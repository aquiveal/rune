# Changelog v1.2.1

## Improvements

### Logging Infrastructure
* **Migration to structlog for standardized logging**
  Replaced the internal custom logging implementation with `structlog` to provide structured, flexible logging output and simplified configuration imports. This change ensures consistent log formatting across the codebase.
  Commits: [b3f7d26](https://github.com/aquiveal/rune/commit/b3f7d26a), [e0bcf4c](https://github.com/aquiveal/rune/commit/e0bcf4cf), [3a3b296](https://github.com/aquiveal/rune/commit/3a3b296a)
