---
description: "Managing npm dependencies and type definitions."
globs: ["package.json", "*.ts", "*.tsx"]
---
# Dependency Management

## 🎯 Directives
- ALWAYS place `@types/*` packages in `devDependencies`, NEVER in `dependencies`.
- ALWAYS place `typescript` in `devDependencies`.
- ALWAYS ensure the major and minor versions of a library match its `@types` package.
- ALWAYS isolate third-party dependencies behind custom interfaces (Adapter Pattern).
- NEVER leak third-party types into the core domain model.

## 📝 Examples
### ✅ DO
```json
{
  "dependencies": {
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "@types/lodash": "^4.14.197",
    "typescript": "^5.0.0"
  }
}
```
### ❌ DON'T
```json
{
  "dependencies": {
    "@types/lodash": "^4.14.197",
    "typescript": "^5.0.0"
  }
}