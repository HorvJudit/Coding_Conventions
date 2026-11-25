# JavaScript/TypeScript Specific Rules & Examples

These rules supplement the `core_conventions.md` for JavaScript and TypeScript projects.

## 1. Data Structures & Variables [JS-DATA]
- **[JS-DATA-01] MUST:** Always use `const` for variable declarations by default. 
**EXCEPTION:** Only use `let` if the variable's value needs to be reassigned.
- **[JS-DATA-02] NEVER:** Never use the `var` keyword for variable declarations under any circumstances.
- **[JS-DATA-03] MUST:** Use object destructuring to extract values from objects or arrays to improve readability and enforce explicit data usage.

```javascript
// BAD [JS-DATA-03]
const userProfile = { username: "admin", accessLevel: 5 };
const username = userProfile.username;
const accessLevel = userProfile.accessLevel;

function displayUserRole(user) {
    console.log(user.accessLevel);
}

// GOOD [JS-DATA-03]
const userProfile = { username: "admin", accessLevel: 5 };
const { username, accessLevel } = userProfile;

function displayUserRole({ accessLevel }) {
    console.log(accessLevel);
}
```

## 2. Typing and Documentation [JS-DOCS]
- **[JS-DOCS-01] MUST:** In TypeScript projects, provide explicit type annotations (`type` or `interface`) for all function parameters and return values. Avoid using `any`.
- **[JS-DOCS-02] MUST:** Use a consistent JSDoc standard for documentation containing full descriptions, parameters, and return types for all functions.
**EXCEPTION:** Internal functions (e.g., helper functions not exported from the module) are exempt from the full format requirement and may use a simple one-line summary instead.

## 3. Error Handling and Async [JS-ERR]
- **[JS-ERR-01] MUST:** Always handle Promise rejections. When using `async/await`, wrap the await calls in `try/catch` blocks or use `.catch()` for chained Promises to prevent Unhandled Promise Rejections.
- **[JS-ERR-02] MUST:** Prefer `async/await` syntax over raw `.then().catch()` chains for better readability.

```javascript
# BAD [JS-ERR-01, JS-ERR-02, CORE-FLOW-01]
function fetchUserData(userId) {
    api.getUser(userId).then(user => {
        if(user) {
            processUser(user);
        }
    }); // Missing error handling
}

# GOOD [JS-ERR-01, JS-ERR-02, CORE-FLOW-01]
async function fetchUserData(userId) {
    if (!userId) {
        throw new Error("User ID is required."); // Early return
    }
    
    try {
        const user = await api.getUser(userId);
        return processUser(user);
    } catch (error) {
        logger.error(`Failed to fetch user: ${error.message}`);
        throw error;
    }
}
```

## 4. Module Structure and Encapsulation [JS-MOD]

- **[JS-MOD-01] MUST:** Modules must expose a clear and concise public API. Use the `export` keyword only for functions, classes, or constants that are intended to be consumed by other modules. 
- **[JS-MOD-02] MUST:** Hide internal state in modules. Any helper function or variable that is only used locally within the file must not be exported.
- **[JS-MOD-03] MUST:** When using classes, strictly encapsulate internal state and methods. Use the private field syntax (`#`) in ES6 JavaScript, or the `private` modifier in TypeScript.
- **[JS-MOD-04] SHOULD:** Prefer functional programming patterns and plain ES modules over complex Object-Oriented class hierarchies. Use standalone functions instead of classes unless you need to maintain complex internal state.

```javascript
// BAD [JS-MOD-02, JS-MOD-03]
export function _formatDateHelper(date) { ... } // Should not be exported if internal

class UserService {
    dbConnection = null; // Public by default, exposing internal state
}

// GOOD [JS-MOD-01, JS-MOD-02, JS-MOD-03]
// Internal helper (not exported)
function formatDateHelper(date) { ... }

// Public API
export async function processUser(user) { ... }

class UserService {
    #dbConnection; // Strictly private (ES6)
    // private dbConnection; // (in TypeScript)
    
    constructor(db) {
        this.#dbConnection = db;
    }
}
```