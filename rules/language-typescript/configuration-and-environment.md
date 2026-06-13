---
description: "TypeScript compiler and environment configuration."
globs: ["tsconfig.json", "*.ts", "*.tsx"]
---
# Configuration and Environment

## 🎯 Directives
- ALWAYS enable `strict: true` in `tsconfig.json`.
- ALWAYS enable `noImplicitAny: true` and `strictNullChecks: true`.
- ALWAYS configure `sourceMap: true` for debugging.
- ALWAYS use `transpileOnly` or tools like `swc`/`esbuild` for fast development builds.
- NEVER use command-line flags for compiler options; ALWAYS use `tsconfig.json`.
- ALWAYS validate environment variables at startup using a schema validation library (e.g., Zod).

## 📝 Examples
### ✅ DO
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```
### ❌ DON'T
```json
{
  "compilerOptions": {
    "strict": false
  }
}