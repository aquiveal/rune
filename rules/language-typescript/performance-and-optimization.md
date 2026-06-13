---
description: "Performance optimization and efficiency guidelines."
globs: ["*.ts", "*.tsx"]
---
# Performance and Optimization

## 🎯 Directives
- ALWAYS prioritize code readability and maintainability over premature optimization.
- ALWAYS measure performance before applying optimizations.
- ALWAYS use asynchronous non-blocking I/O operations (`async`/`await`).
- ALWAYS use `Promise.all` for independent concurrent asynchronous operations.
- NEVER block the Node.js event loop with heavy synchronous computations.
- ALWAYS paginate or stream large datasets instead of loading them entirely into memory.

## 📝 Examples
### ✅ DO
```typescript
const [users, posts] = await Promise.all([getUsers(), getPosts()]);
```
### ❌ DON'T
```typescript
const users = await getUsers();
const posts = await getPosts(); // Unnecessarily sequential