---
description: "Error handling and exception management."
globs: ["*.ts", "*.tsx"]
---
# Error Handling

## 🎯 Directives
- ALWAYS use custom Error classes that extend `Error` for domain-specific failures.
- ALWAYS prefer returning a `Result` or `Either` monad for expected business logic failures instead of throwing exceptions.
- NEVER use exceptions for normal control flow.
- NEVER return `null` or `undefined` to indicate an error; return an explicit failure state or empty collection.
- ALWAYS wrap third-party API calls in `try/catch` and map their exceptions to domain-specific errors.

## 📝 Examples
### ✅ DO
```typescript
type Result<T, E = Error> = { success: true; value: T } | { success: false; error: E };

function getUser(id: string): Result<User, UserNotFoundError> { ... }
```
### ❌ DON'T
```typescript
function getUser(id: string): User | null {
  // Returns null on error, forcing null checks everywhere
}