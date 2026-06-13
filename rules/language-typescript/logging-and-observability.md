---
description: "Logging, monitoring, and observability standards."
globs: ["*.ts", "*.tsx"]
---
# Logging and Observability

## 🎯 Directives
- ALWAYS use a structured logging library (e.g., Pino, Winston) instead of `console.log`.
- ALWAYS include contextual metadata (e.g., request ID, user ID) in log entries.
- ALWAYS log at appropriate levels (`error`, `warn`, `info`, `debug`).
- NEVER log sensitive information (PII, passwords, tokens).
- ALWAYS instrument critical business paths with metrics and tracing.

## 📝 Examples
### ✅ DO
```typescript
logger.info({ userId: user.id, action: 'login' }, 'User logged in successfully');
```
### ❌ DON'T
```typescript
console.log(`User ${user.id} logged in successfully`);