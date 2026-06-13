---
description: "Node.js logging, metrics, and observability"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Logging & Observability

## 🎯 Directives

### Logging
- ALWAYS output logs as well-formed JSON objects.
- ALWAYS keep JSON log objects shallow (maximum 1 or 2 levels deep) for easy indexing.
- ALWAYS include standard metadata: `@timestamp`, `app`, `environment`, `severity`, `type`, and `fields`.
- ALWAYS restrict log severities to standard levels: `error`, `warn`, `info`, `verbose`, `debug`, `silly`.

### Metrics & Tracing
- ALWAYS capture numeric data over time using StatsD format or similar time-series metrics.
- ALWAYS prefix metric names with the application's unique name (e.g., `web-api.inbound.request-time`).
- ALWAYS propagate trace context to upstream services using B3 HTTP headers (`X-B3-TraceId`, etc.).
- ALWAYS expose a dedicated `/health` HTTP endpoint.

### Health Checks
- ALWAYS return HTTP 500 if the primary datastore is unreachable.
- ALWAYS return HTTP 200 with a `DEGRADED` status if a secondary/caching datastore is unreachable.

## 📝 Examples

### ✅ DO: Structured JSON Logging
```javascript
console.log(JSON.stringify({
  '@timestamp': new Date().toISOString(),
  app: 'web-api',
  environment: process.env.NODE_ENV,
  severity: 'error',
  type: 'request-failure',
  fields: { path: req.url, error: err.message }
}));