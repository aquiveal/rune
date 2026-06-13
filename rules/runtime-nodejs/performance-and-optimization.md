---
description: "Node.js performance, streams, and optimization"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Performance & Optimization

## 🎯 Directives

### Streams & I/O
- ALWAYS use Streams (`createReadStream`, `createWriteStream`) instead of buffered APIs (`readFile`) for large payloads.
- ALWAYS respect stream backpressure: if `write()` returns `false`, wait for the `drain` event.
- ALWAYS use `pipeline()` from `node:stream/promises` to connect streams safely; NEVER use raw `.pipe()`.

### V8 Optimization
- ALWAYS maintain consistent data types within arrays to prevent V8 de-optimization.
- NEVER use the `delete` keyword on an array element; it creates a sparse array.
- ALWAYS initialize object properties in the exact same order in constructors to share V8 Hidden Classes.
- NEVER add properties to an object after instantiation.

### Caching & Offloading
- ALWAYS offload CPU-intensive tasks (TLS termination, gzip) to a reverse proxy (HAProxy/Nginx).
- ALWAYS use LRU caches with byte-length limits for in-memory caching.
- ALWAYS implement Asynchronous Request Batching for high-load APIs to prevent duplicate concurrent queries.

## 📝 Examples

### ✅ DO: Safe Stream Piping
```javascript
import { pipeline } from 'node:stream/promises';
import { createReadStream, createWriteStream } from 'node:fs';

await pipeline(
  createReadStream('input.txt'),
  createWriteStream('output.txt')
);
```

### ❌ DON'T: V8 De-optimization
```javascript
function User(name) {
  this.name = name;
}
const u = new User("Alice");
u.age = 30; // DE-OPTIMIZED: Alters hidden class after instantiation