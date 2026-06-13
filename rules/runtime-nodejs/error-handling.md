---
description: "Node.js error handling and resilience"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Error Handling

## 🎯 Directives

### Process Lifecycle
- ALWAYS listen to `process.on('uncaughtException')` and `process.on('unhandledRejection')`, log the error, and synchronously `process.exit(1)`.
- NEVER attempt to continue execution after an uncaught exception.
- ALWAYS implement Graceful Shutdown on `SIGTERM`/`SIGINT`.

### Async Errors
- ALWAYS wrap `await` calls in `try...catch` blocks.
- ALWAYS use `return await` if returning a Promise inside a `try` block to catch rejections locally.
- ALWAYS attach an `'error'` event listener to all `EventEmitter` and `Stream` instances.

### Error Types & Retries
- ALWAYS differentiate errors using `.code` or `instanceof`, NEVER by parsing `.message`.
- ALWAYS implement Exponential Backoff with Jitter for network retries to prevent Thundering Herd.
- ALWAYS use the Circuit Breaker pattern for external API dependencies.

## 📝 Examples

### ✅ DO: Uncaught Exception Handling
```javascript
process.on('uncaughtException', (err) => {
  console.error('Fatal Exception:', err);
  process.exit(1); 
});
```

### ❌ DON'T: The "return await" Trap
```javascript
async function errorNotCaught() {
  try {
    return delayError(1000); // Rejection escapes the catch block
  } catch (err) {
    console.error(err);
  }
}