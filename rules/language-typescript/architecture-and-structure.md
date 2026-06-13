---
description: "Architectural guidelines and project structure for TypeScript applications."
globs: ["*.ts", "*.tsx"]
---
# Architecture and Structure

## 🎯 Directives
- ALWAYS separate business logic (Domain) from infrastructure (DB, UI, Frameworks).
- ALWAYS use Dependency Injection to pass dependencies into classes or functions.
- ALWAYS program to interfaces, not concrete implementations.
- ALWAYS group files by feature or use case (Vertical Slicing), NOT by technical type (e.g., controllers, services).
- ALWAYS keep functions small (under 20 lines) and classes focused on a single responsibility.
- ALWAYS apply the Dependency Inversion Principle: high-level modules MUST NOT depend on low-level modules.
- NEVER mix orchestration (high-level) and execution (low-level) in the same function.

## 📝 Examples
### ✅ DO
```typescript
// src/features/createUser/
export class CreateUserUseCase {
  constructor(private userRepo: IUserRepository) {}
}
```
### ❌ DON'T
```typescript
// src/services/UserService.ts
import { PostgresUserRepo } from '../repos/PostgresUserRepo';
export class UserService {
  private repo = new PostgresUserRepo();
}