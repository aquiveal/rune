---
description: "Security practices and data validation."
globs: ["*.ts", "*.tsx"]
---
# Security and Validation

## 🎯 Directives
- ALWAYS validate and sanitize all external input at the system boundaries using a schema validation library (e.g., Zod, Yup).
- NEVER trust client-side data.
- ALWAYS use parameterized queries or ORMs to prevent SQL injection.
- NEVER store plain-text passwords; ALWAYS use strong hashing algorithms (e.g., bcrypt, Argon2).
- ALWAYS implement rate limiting and authentication/authorization on API endpoints.
- NEVER use `eval()` or `Function()` with dynamic strings.

## 📝 Examples
### ✅ DO
```typescript
import { z } from 'zod';
const UserSchema = z.object({ email: z.string().email(), age: z.number().min(18) });
const userData = UserSchema.parse(req.body);
```
### ❌ DON'T
```typescript
const userData = req.body as User; // Unsafe, no runtime validation