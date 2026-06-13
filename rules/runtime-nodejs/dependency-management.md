---
description: "Node.js dependency management and package.json"
globs: "package.json, package-lock.json"
---
# Dependency Management

## 🎯 Directives

### Package Configuration
- ALWAYS specify the `engines` field in `package.json` targeting a specific Node.js LTS release.
- ALWAYS set `"private": true` in `package.json` for applications to prevent accidental publication.
- ALWAYS use explicit file extensions in `require()` or `import` calls (e.g., `./foo.js`).

### Versioning & Upgrades
- ALWAYS adhere strictly to Semantic Versioning (SemVer): Major (breaking), Minor (feature), Patch (fix).
- ALWAYS perform piecemeal dependency upgrades to isolate regressions.
- ALWAYS commit `package-lock.json` in applications, but NEVER in published reusable npm packages.

### CI/CD & Docker
- ALWAYS use `npm ci --only=production` in CI/CD and Docker builds for deterministic dependency trees.
- ALWAYS use multi-stage Docker builds, copying `node_modules` from a build stage to a minimal Alpine runtime stage.

## 📝 Examples

### ✅ DO: Multi-stage Dockerfile
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS release
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
CMD ["node", "server.js"]