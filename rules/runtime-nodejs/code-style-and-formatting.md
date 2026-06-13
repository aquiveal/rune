---
description: "Node.js code style and formatting"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Code Style & Formatting

## 🎯 Directives

### General
- ALWAYS use early returns to prevent deep nesting (Callback Hell).
- ALWAYS use `const` by default, `let` for mutation, and NEVER use `var`.
- ALWAYS use Arrow Functions (`() => {}`) to preserve lexical `this` context in callbacks.
- ALWAYS use named functions for callbacks to ensure readable stack traces and V8 profiling.

### Asynchronous Patterns
- ALWAYS place the callback as the last argument in asynchronous APIs.
- ALWAYS reserve the first argument of a callback for the `Error` object (Error-first pattern).
- ALWAYS prefer `async/await` over raw Promise chaining.
- ALWAYS use `Promise.all()` or `Promise.allSettled()` for concurrent execution.

## 📝 Examples

### ✅ DO: Early Returns
```javascript
function processFile(filename, cb) {
  exists(filename, (err, exists) => {
    if (err) return cb(err);
    if (!exists) return cb(new Error('Not found'));
    // Proceed...
  });
}
```

### ❌ DON'T: Deep Nesting
```javascript
function processFile(filename, cb) {
  exists(filename, (err, exists) => {
    if (!err) {
      if (exists) {
        // Proceed...
      }
    }
  });
}