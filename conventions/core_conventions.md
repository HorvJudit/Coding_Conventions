# Core Architecture & Design Principles

These rules apply universally to all projects, regardless of the programming language. They must be concatenated with the language-specific ruleset during the AI assisted coding or AI review process.

## 1. Architecture & Function Design [CORE-ARCH]
- **[CORE-ARCH-01] MUST:** Design functions to be deterministic (Pure Functions). The output must depend solely on the input parameters. Do not rely on or mutate global state.
- **[CORE-ARCH-02] MUST:** Do not mutate input parameters by reference. Always return the modified data as a new value to ensure predictability.
- **[CORE-ARCH-03] MUST:** Apply Dependency Injection. External resources (database connections, configuration files, loggers) must be passed as parameters to make testing and mocking easier.
- **[CORE-ARCH-04] MUST:** Adhere to the Single Responsibility Principle (SRP). If a function name implies multiple actions (e.g., uses "and"), or if its body cannot fit on a single screen, it must be refactored into smaller, well-named sub-functions.
- **[CORE-ARCH-05] MUST:** Adhere to the Don't Repeat Yourself (DRY) principle. Avoid code duplication. If the exact same logic appears in multiple places, extract it into a shared, reusable function or module.

## 2. Error Handling & Control Flow [CORE-FLOW]
- **[CORE-FLOW-01] MUST:** Apply the Fail Fast principle using Early Returns / Guard Clauses. Validate edge cases at the very beginning of the function and throw an error or return immediately to avoid deep nesting (if-else hell).
- **[CORE-FLOW-02] NEVER:** Do not suppress errors (silent errors). Never return `null`, `None`, or empty structures on failure unless explicitly expected by the business logic, handled by the caller, and documented.
- **[CORE-FLOW-03] SHOULD:** Implement a data validation layer for all incoming data from external systems (APIs, databases). Verify presence (null checks), type matching, and empty states.

## 3. Commenting & Documentation [CORE-DOCS]
- **[CORE-DOCS-01] NEVER:** Do not write inline comments explaining *what* the code does. The code must be self-documenting through clear naming.
- **[CORE-DOCS-02] MUST:** Use comments exclusively to explain *why* a specific approach was taken (e.g., underlying business decisions, workarounds, or hacks).
- **[CORE-DOCS-03] NEVER:** Do not use comments to separate logical blocks within a single function. If a block needs a comment to be understood or separated, extract it into a separate, well-named function.
**EXCEPTION:** High-level Orchestrator or Pipeline functions (e.g., main()) that purely delegate to other sub-functions may use comments to separate logical phases. This is permitted to prevent creating wrapper functions that would require passing excessive amounts of parameters (e.g., avoiding "15-parameter monster" functions).