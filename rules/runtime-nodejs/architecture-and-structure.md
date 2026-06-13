---
description: "Node.js architectural patterns and structure"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Architecture & Structure

## 🎯 Directives

### Core Principles
- ALWAYS follow the Unix Philosophy: write small, focused modules that do one thing well.
- ALWAYS use ECMAScript Modules (ESM) as the default standard (`"type": "module"`).
- ALWAYS prefer Named Exports over Default Exports for better tree-shaking and refactoring.
- ALWAYS use Dependency Injection (DI) to decouple modules and improve testability.

### Scalability & Concurrency
- ALWAYS design for horizontal scalability (Scale Cube) and statelessness. Store session state in Redis, not memory.
- ALWAYS offload CPU-bound tasks to `worker_threads` or child processes.
- ALWAYS use Streams for data processing and I/O to minimize memory footprint.
- ALWAYS implement Graceful Shutdown: listen for `SIGTERM`/`SIGINT`, stop accepting connections, finish requests, close DB, and exit.

### Microservices & Integration
- ALWAYS enforce the Data Ownership principle: each microservice MUST have its own independent database.
- ALWAYS use an API Gateway/BFF for semantic integration and a Message Broker (RabbitMQ/Redis) for asynchronous state changes.
- ALWAYS use Server-Sent Events (SSE) for unidirectional real-time data and WebSockets for bidirectional communication.

## 📝 Examples

### ✅ DO: Dependency Injection
```javascript
export class BlogService {
  constructor(db) {
    this.db = db;
  }
  getPosts() {
    return this.db.query('SELECT * FROM posts');
  }
}
```

### ❌ DON'T: Tight Coupling
```javascript
import { db } from './db.js';
export class BlogService {
  getPosts() {
    return db.query('SELECT * FROM posts');
  }
}