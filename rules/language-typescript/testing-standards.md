---
description: "Automated testing standards and practices."
globs: ["*.test.ts", "*.spec.ts", "*.test.tsx", "*.spec.tsx"]
---
# Testing Standards

## 🎯 Directives
- ALWAYS write tests using the Arrange-Act-Assert (Given-When-Then) pattern.
- ALWAYS ensure tests are deterministic and independent of each other.
- ALWAYS use a fresh fixture/state for every test (e.g., using `beforeEach`).
- ALWAYS mock external dependencies (I/O, network, time) to keep tests fast and reliable.
- ALWAYS prioritize integration tests over isolated unit tests for higher confidence.
- NEVER test internal implementation details; test observable behavior and public APIs.
- NEVER use shared mutable state across tests.

## 📝 Examples
### ✅ DO
```typescript
test('calculates total with tax', () => {
  // Arrange
  const cart = new Cart([{ price: 100 }]);
  // Act
  const total = cart.calculateTotal(0.1);
  // Assert
  expect(total).toBe(110);
});
```
### ❌ DON'T
```typescript
test('calculates total', () => {
  cart.addItem({ price: 100 });
  expect(cart.calculateTotal(0.1)).toBe(110);
  cart.addItem({ price: 50 }); // State bleeds into next assertion
  expect(cart.calculateTotal(0.1)).toBe(165);
});