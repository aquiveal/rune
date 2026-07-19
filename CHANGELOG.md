# Changelog v2.1.5

## Fixes

* **Corrected WorldlineSettings Import Path**
  The import path for `WorldlineSettings` has been updated to correctly reference `worldline.config` instead of the direct `worldline` module. This resolves potential module resolution errors in environments strict about path exports.
  * Commits: [e37e673](https://github.com/aquiveal/rune/commit/e37e673a), [cda114b](https://github.com/aquiveal/rune/commit/cda114b6)
