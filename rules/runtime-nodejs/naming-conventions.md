---
description: "Node.js naming conventions"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Naming Conventions

## 🎯 Directives

- ALWAYS use `camelCase` for variables, functions, and instances.
- ALWAYS use `PascalCase` for classes, interfaces, and type aliases.
- ALWAYS use `UPPER_SNAKE_CASE` for global constants and environment variables.
- ALWAYS use `kebab-case` for filenames and directory names (e.g., `user-controller.js`).
- ALWAYS prefix private class fields with `#` (native private fields) or `_` (if using older conventions).
- ALWAYS name callback functions to ensure distinct and readable stack traces during debugging.

## 📝 Examples

### ✅ DO: Named Callbacks and Kebab-case Files
```javascript
// file: process-data.js
import { readFile } from 'node:fs';

export function processData(filePath, cb) {
  readFile(filePath, 'utf8', function onFileRead(err, data) {
    if (err) return cb(err);
    cb(null, data);
  });
}