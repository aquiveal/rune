---
description: "Node.js documentation and comments standards"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Documentation & Comments

## 🎯 Directives

- ALWAYS document public APIs, exported functions, and classes using JSDoc or TSDoc standards.
- ALWAYS explain *why* a specific architectural decision was made in comments, not just *what* the code does.
- ALWAYS document expected environment variables in a `.env.example` file or README.
- NEVER leave commented-out dead code in the repository.

## 📝 Examples

### ✅ DO: JSDoc for Public APIs
```javascript
/**
 * Fetches a user by their ID.
 * @param {string} id - The UUID of the user.
 * @returns {Promise<User>} The user object.
 * @throws {NotFoundError} If the user does not exist.
 */
export async function getUser(id) {
  // ...
}