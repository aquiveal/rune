---
description: "Avoid common TypeScript and software design anti-patterns."
globs: ["*.ts", "*.tsx"]
---
# Anti-Patterns

## 🎯 Directives
- NEVER use `any`. ALWAYS use `unknown` if the type is truly dynamic, and narrow it.
- NEVER use `as Type` assertions to bypass the type checker. ALWAYS use type annotations or type guards.
- NEVER use `enum`. ALWAYS use union types of string literals (e.g., `type Status = 'open' | 'closed'`).
- NEVER use non-null assertions (`!`). ALWAYS handle `null` or `undefined` explicitly.
- NEVER create "God Classes" or "Helper" classes. ALWAYS adhere to the Single Responsibility Principle.
- NEVER use primitive obsession. ALWAYS wrap domain concepts in Value Objects.
- NEVER use magic numbers or strings. ALWAYS extract them into named constants.
- NEVER use nested `if/else` or `switch` statements for type checking. ALWAYS use polymorphism or object mapping.

## 📝 Examples
### ✅ DO
```typescript
type Status = 'active' | 'inactive';
function handleStatus(status: Status) { ... }
```
### ❌ DON'T
```typescript
enum Status { Active, Inactive }
function handleStatus(status: any) { ... }