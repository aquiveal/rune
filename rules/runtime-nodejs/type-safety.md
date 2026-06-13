---
description: "Node.js type safety and TypeScript configuration"
globs: "**/*.{ts,tsx}, tsconfig.json"
---
# Type Safety

## 🎯 Directives

### TypeScript Configuration
- ALWAYS configure `tsconfig.json` with `"module": "NodeNext"` and `"moduleResolution": "NodeNext"` for modern Node.js.
- ALWAYS enable `"verbatimModuleSyntax": true` to ensure imports/exports map directly to emitted JavaScript.
- ALWAYS include `@types/node` as a development dependency.

### Execution
- ALWAYS use `tsx` as a loader for on-the-fly TypeScript execution in development.
- ALWAYS pre-transpile TypeScript before production deployment to avoid runtime performance penalties.
- ALWAYS use explicit file extensions (`.js`) in relative imports within TypeScript files when using `NodeNext`.

## 📝 Examples

### ✅ DO: Modern tsconfig.json
```json
{
  "compilerOptions": {
    "target": "es2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "verbatimModuleSyntax": true,
    "strict": true
  }
}
```

### ❌ DON'T: Legacy Configuration
```json
{
  "compilerOptions": {
    "target": "es6",
    "module": "CommonJS",
    "moduleResolution": "node"
  }
}