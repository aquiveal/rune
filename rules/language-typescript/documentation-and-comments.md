---
description: "Rules for writing comments and documentation."
globs: ["*.ts", "*.tsx"]
---
# Documentation and Comments

## 🎯 Directives
- ALWAYS write code that explains itself through expressive naming and structure.
- ALWAYS use comments to explain *WHY* a decision was made, NEVER *WHAT* the code is doing.
- ALWAYS use TSDoc (`/** ... */`) for public APIs, interfaces, and complex functions.
- NEVER leave commented-out code. Delete it; version control will remember it.
- NEVER use redundant comments that restate the method signature.
- NEVER include type information in TSDoc tags (e.g., `@param {string} name`); rely on TypeScript annotations.

## 📝 Examples
### ✅ DO
```typescript
/**
 * Calculates the final price including regional tax.
 * @param basePrice The pre-tax price
 */
function calculateTotal(basePrice: number): number { ... }
```
### ❌ DON'T
```typescript
// This function calculates the total
// @param {number} basePrice
function calculateTotal(basePrice: number): number { ... }