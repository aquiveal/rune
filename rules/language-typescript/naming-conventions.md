---
description: "Naming conventions for variables, functions, classes, and files."
globs: ["*.ts", "*.tsx"]
---
# Naming Conventions

## 🎯 Directives
- ALWAYS use `camelCase` for variables, functions, and class instances.
- ALWAYS use `PascalCase` for classes, interfaces, types, and enums.
- ALWAYS use `UPPER_SNAKE_CASE` for global constants.
- ALWAYS use kebab-case for file and directory names (e.g., `user-controller.ts`).
- ALWAYS use intention-revealing names. Avoid abbreviations and single-letter variables (except in short loops).
- ALWAYS prefix boolean variables with `is`, `has`, `can`, or `should`.
- NEVER use Hungarian notation or type prefixes (e.g., `IUser`, `strName`).

## 📝 Examples
### ✅ DO
```typescript
const isActive = true;
class UserAccount { ... }
const MAX_RETRIES = 3;
```
### ❌ DON'T
```typescript
const active = true;
class user_account { ... }
const maxRetries = 3;