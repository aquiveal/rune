---
description: "Node.js anti-patterns to avoid"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Anti-Patterns

## 🎯 Directives

### Asynchronous & Event Loop
- NEVER block the Event Loop with synchronous I/O (`readFileSync`) or heavy CPU tasks in the main thread.
- NEVER introduce Zalgo: APIs MUST be 100% synchronous or 100% asynchronous. Use `process.nextTick()` to defer synchronous returns in async APIs.
- NEVER use `Array.prototype.forEach` with `async` callbacks for sequential execution; ALWAYS use `for...of`.
- NEVER create infinite recursive Promise chains; use `while(true)` with `await` instead.
- NEVER swallow errors or use string rejections. ALWAYS reject with `Error` instances.

### Architecture & State
- NEVER mutate shared global state or monkey-patch imported modules.
- NEVER use unbounded in-memory caches (e.g., `new Map()`); ALWAYS use LRU caches with size limits.
- NEVER store user sessions or application state in the memory of the Node.js process; use Redis.
- NEVER use the `cluster` module for scaling if a reverse proxy (like HAProxy/Nginx) can be used instead.

### Security & Data
- NEVER use naive shallow cloning techniques that blindly copy `__proto__` properties (Prototype Pollution).
- NEVER hardcode sensitive credentials, API keys, or hostnames in source code.

## 📝 Examples

### ❌ DON'T: Zalgo (Inconsistent Asynchrony)
```javascript
function fetchUser(id, callback) {
  if (id <= 0) {
    return callback(new TypeError('id must be > 0')); // Synchronous
  }
  db.query('SELECT * FROM users WHERE id = ?', [id], callback); // Asynchronous
}
```

### ✅ DO: Consistent Asynchrony
```javascript
function fetchUser(id, callback) {
  if (id <= 0) {
    return process.nextTick(() => callback(new TypeError('id must be > 0')));
  }
  db.query('SELECT * FROM users WHERE id = ?', [id], callback);
}
