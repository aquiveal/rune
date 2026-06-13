---
description: "Use this when writing tests, configuring test runners (Jest/Vitest), or structuring test directories in Node.js projects."
globs: "**/*.{spec,test}.{ts,js}, jest.config.*, vitest.config.*, tests/**/*"
---
# Testing Standards

## 🎯 Directives

### Architecture & Structure
- ALWAYS separate tests into distinct categories: `unit`, `integration`, `e2e`, `contract`, and `performance` within a root `tests/` directory.
- ALWAYS mirror the `src/` directory structure inside `tests/unit/`.
- ALWAYS use `.spec.ts` or `.test.ts` suffixes for test files.
- ALWAYS use `.int.spec.ts` or `.int.test.ts` for integration tests to distinguish them from unit tests.
- ALWAYS place unit-specific mocks in a `__fixtures__` directory next to the test file.
- ALWAYS place global shared fixtures in `tests/fixtures/`.
- ALWAYS separate integration tests into `internal/` (Database, Redis, Message Queues) and `external/` (3rd Party APIs).
- ALWAYS use a Page Object Model (POM) for E2E tests (`e2e/pages/`).
- NEVER mix unit tests and integration tests in the same file or directory.
- NEVER place test files alongside source code in the `src/` directory; ALWAYS keep them in the `tests/` directory.

### Testing Patterns & Best Practices
- ALWAYS structure tests strictly using the Arrange-Act-Assert (AAA) pattern.
- ALWAYS favor Dependency Injection (DI) to isolate dependencies over global module mocking.
- ALWAYS restore/clear mocks, spies, and stubs in `afterEach` or `afterAll` hooks to prevent test pollution.
- ALWAYS use strict equality assertions (e.g., `expect(a).toStrictEqual(b)` in Jest/Vitest) to prevent unintended type coercion.
- ALWAYS name all functions (avoid anonymous functions) to ensure they appear clearly in V8 profiler logs if profiling is needed.
- NEVER use both a `done` callback and return a Promise in the same test function.
- NEVER use manual timeouts (e.g., `waitForTimeout`) in Playwright E2E tests; ALWAYS use web-first assertions (e.g., `await expect(locator).toBeVisible()`).
- ALWAYS use resilient, user-centric locators in Playwright such as `page.getByRole()`, `page.getByLabel()`, `page.getByText()`, and `page.getByTestId()`.
- ALWAYS seed unique data for form inputs in E2E tests (e.g., using `Date.now()`) to avoid unique constraint violations across test runs.

## 📝 Examples

### ✅ DO: Unit Test with Dependency Injection and AAA Pattern

```typescript
// tests/unit/services/auth.service.spec.ts
import { describe, it, expect, vi, afterEach } from 'vitest'; // or from '@jest/globals'
import { AuthService } from '../../../src/services/auth.service';
import rawUserData from './__fixtures__/raw-user-data.json';

describe('AuthService', () => {
  afterEach(() => {
    vi.restoreAllMocks(); // ALWAYS restore mocks
  });

  it('should authenticate user successfully', () => {
    // Arrange
    const mockDb = {
      findUser: vi.fn().mockReturnValue(rawUserData)
    };
    const authService = new AuthService(mockDb); // Dependency Injection

    // Act
    const result = authService.login(rawUserData.username, rawUserData.password);

    // Assert
    expect(result).toStrictEqual(true); // Strict equality
    expect(mockDb.findUser).toHaveBeenCalledTimes(1);
  });
});
```

### ✅ DO: Playwright E2E Test with Web-First Assertions

```typescript
// tests/e2e/flow-checkout.spec.ts
import { test, expect } from '@playwright/test';

test('Checkout flow', async ({ page }) => {
  // Arrange
  await page.goto('http://localhost:3000');
  
  // Act
  await page.getByRole('link', { name: 'Cart' }).click();
  const seed = Date.now().toString();
  await page.getByRole('textbox', { name: 'email' }).fill(`test${seed}@example.com`);
  await page.getByRole('button', { name: 'Checkout' }).click();

  // Assert
  const successMessage = page.getByTestId('success-message');
  await expect(successMessage).toBeVisible(); // Web-first assertion, auto-waits
});
```

### ❌ DON'T: Global Mocking without Cleanup and Loose Assertions

```typescript
// src/services/auth.service.spec.ts
// DON'T place tests inside the src/ directory.
import { describe, it, expect, vi } from 'vitest';
import { AuthService } from './auth.service';
import * as db from './db';

// DON'T mock globally without restoring
vi.mock('./db', () => ({
  findUser: vi.fn()
}));

describe('AuthService', () => {
  it('should authenticate', () => {
    // DON'T skip Arrange-Act-Assert structure
    const authService = new AuthService();
    // DON'T use loose equality if strict is available
    expect(authService.login('user', 'pass')).toEqual(true); 
  });
});
```

## 📂 Required Directory Structure

ALWAYS adhere to the following directory structure for tests:

```text
my-node-project/
├── src/                        # Source code
├── tests/
│   ├── unit/                   # 1-to-1 Mirror of src/
│   │   ├── services/
│   │   │   ├── auth.service.spec.ts
│   │   │   └── __fixtures__/   # Unit-specific JSON mocks
│   │   │       └── raw-user-data.json
│   │   └── utils/
│   │       └── logger.spec.ts
│   ├── integration/
│   │   ├── internal/           # Database / Redis / Message Queue
│   │   │   ├── setup.ts        # Database seeding/migrations for tests
│   │   │   └── user.repository.int.spec.ts
│   │   └── external/           # 3rd Party APIs (Sandbox)
│   │       ├── __recordings__/ # Polly.js / Nock Cassettes
│   │       │   └── stripe-checkout.har
│   │       ├── stripe.service.int.spec.ts
│   │       └── openai.service.int.spec.ts
│   ├── e2e/                    # Playwright / Cypress (Mirrors Next.js app router structure)
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   └── login/
│   │   │   │       └── login.spec.ts
│   │   │   └── dashboard/
│   │   │       └── dashboard.spec.ts
│   │   └── _pages/             # Page Object Model (POM)
│   │       ├── login.page.ts
│   │       └── dashboard.page.ts
│   ├── contract/               # API Consumer/Provider verification
│   │   └── pacts/              # Pact JSON files
│   ├── performance/            # Load testing
│   │   └── k6-load-test.js
│   └── fixtures/               # GLOBAL SHARED FIXTURES
│       ├── images/             # Sample images for upload tests
│       ├── pdfs/               # Sample docs
│       └── global-constants.ts
├── jest.config.js              # or vitest.config.ts
├── playwright.config.ts
└── package.json