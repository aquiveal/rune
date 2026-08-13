## Features

* **Install Documentation Rules via Web URLs**
  * Added the ability to install rules directly from web documentation URLs alongside traditional git repositories.
  * Introduced the `is_web_url` utility and a custom `name` parameter to support this functionality.
  * Updated CLI help text and routing logic to direct requests to `create_rule_from_doc_url`.
  * Commits: [769bd44](https://github.com/aquiveal/rune/commit/769bd445), [bdd4005](https://github.com/aquiveal/rune/commit/bdd40056)
