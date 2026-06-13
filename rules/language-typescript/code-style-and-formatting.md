---
description: "Code style, formatting, and readability standards."
globs: ["*.ts", "*.tsx"]
---
# Code Style and Formatting

## 🎯 Directives
- ALWAYS use Prettier and ESLint for automated formatting and linting.
- ALWAYS use `const` by default. Use `let` only when reassignment is necessary. NEVER use `var`.
- ALWAYS use arrow functions for callbacks and anonymous functions.
- ALWAYS use object destructuring and spread operators for object manipulation.
- ALWAYS keep lines under 100-120 characters.
- ALWAYS place the caller function immediately above the callee function (Stepdown Rule).
- NEVER use horizontal alignment for variable assignments.
- ALWAYS use early returns (Guard Clauses) to avoid deep nesting.

## 📝 Examples
### ✅ DO
```typescript
function processUser(user: User): void {
  if (!user.isActive) return;
  // process active user
}
```
### ❌ DON'T
```typescript
function processUser(user: User): void {
  if (user.isActive) {
    // process active user
  }
}