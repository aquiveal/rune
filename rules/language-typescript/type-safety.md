---
description: "Advanced TypeScript type safety and type-level programming."
globs: ["*.ts", "*.tsx"]
---
# Type Safety

## 🎯 Directives
- ALWAYS use explicit return types for functions and methods.
- ALWAYS use Tagged/Discriminated Unions to model mutually exclusive states.
- ALWAYS use `readonly` for arrays and objects that should not be mutated.
- ALWAYS use `Record<K, V>` or `Map` instead of index signatures (`[key: string]: any`).
- ALWAYS use `satisfies` to validate an object's shape without widening its inferred type.
- NEVER use return-only generics (e.g., `function get<T>(): T`); force the caller to assert or validate.
- ALWAYS use exhaustiveness checking (`never`) in `switch` statements over union types.

## 📝 Examples
### ✅ DO
```typescript
type State = 
  | { status: 'loading' }
  | { status: 'success'; data: string }
  | { status: 'error'; error: Error };

function handleState(state: State) {
  if (state.status === 'success') {
    console.log(state.data);
  }
}
```
### ❌ DON'T
```typescript
type State = {
  isLoading: boolean;
  data?: string;
  error?: Error;
};