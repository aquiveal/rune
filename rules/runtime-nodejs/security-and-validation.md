---
description: "Node.js security, validation, and payload handling"
globs: "**/*.{js,ts,cjs,mjs}"
---
# Security & Validation

## 🎯 Directives

### Payload & Deserialization
- ALWAYS enforce a maximum request size limit for all HTTP body parsers (e.g., 1MB).
- NEVER use naive shallow cloning techniques that blindly copy `__proto__` properties (Prototype Pollution).
- ALWAYS validate keys before cloning or explicitly deny `__proto__` and `constructor`.

### Authentication & Authorization
- ALWAYS use HTTPS for Basic Authentication.
- ALWAYS verify JWT expiration (`exp`) manually against the current server time.
- NEVER maintain a session store for JWTs; the token is the source of truth.
- ALWAYS use Challenge-Response handshakes with short TTLs in Redis for non-HTTPS auth.

### Dependencies
- ALWAYS run `npm audit` and fix vulnerabilities.
- ALWAYS wrap abandoned/vulnerable packages to aggressively sanitize input before passing it to the library.

## 📝 Examples

### ✅ DO: Prevent Prototype Pollution
```javascript
const obj = JSON.parse(requestBody);
if ('__proto__' in obj || 'constructor' in obj) {
  throw new Error('Invalid payload');
}
```

### ❌ DON'T: Naive Cloning
```javascript
function shallowClone(obj) {
  const clone = {};
  for (let key of Object.keys(obj)) {
    clone[key] = obj[key]; // Vulnerable to prototype pollution
  }
  return clone;
}