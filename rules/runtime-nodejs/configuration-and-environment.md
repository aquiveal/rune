---
description: "Node.js configuration and environment management"
globs: "**/*.{js,ts,cjs,mjs}, .env*, config/**/*"
---
# Configuration & Environment

## 🎯 Directives

### Environment Variables
- NEVER hardcode sensitive credentials, API keys, or hostnames in source code.
- ALWAYS extract configuration from `process.env`.
- ALWAYS fail fast at startup (`process.exit(1)`) if required environment variables are missing.
- ALWAYS use `NODE_ENV` strictly to define the environment identity (`development`, `staging`, `production`).
- NEVER commit `.env` files to version control.

### Configuration Management
- ALWAYS use a configuration loader that merges environment-specific settings over default fallbacks.
- NEVER use the environment value to hardcode configuration routing (e.g., `if (env === 'staging') db = 'stage-db'`).

## 📝 Examples

### ✅ DO: Fail Fast on Missing Config
```javascript
if (!process.env.DATABASE_URL) {
  console.error("FATAL: DATABASE_URL is required");
  process.exit(1);
}
const db = new Database(process.env.DATABASE_URL);
```

### ❌ DON'T: Hardcoded Credentials
```javascript
const db = new Database('postgres://admin:secret@localhost/db');