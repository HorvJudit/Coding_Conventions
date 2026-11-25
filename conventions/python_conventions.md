# Python Specific Rules & Examples

These rules supplement the `core_conventions.md` for Python projects.

## 1. Data Structures [PY-DATA]
- **[PY-DATA-01] MUST:** Use `Enum` when a variable can only take values from a predefined, finite set (e.g., states, roles).
- **[PY-DATA-02] MUST:** Use `@dataclass` for objects containing multiple related parameters instead of dictionaries, especially when the dictionary keys and value types cannot be strictly defined by Type Hints.

```python
# BAD [PY-DATA-01, PY-DATA-02]
task_config = {"timeout": 30, "retry": 3, "status": "pending"}

# GOOD [PY-DATA-01, PY-DATA-02]
from enum import Enum
from dataclasses import dataclass

class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"

@dataclass
class TaskConfig:
    timeout_seconds: int
    retry_count: int
    status: TaskStatus
```

## 2. Typing and Documentation [PY-DOCS]
- **[PY-DOCS-01] MUST:** Provide explicit Type Hints for all function parameters and return values.
- **[PY-DOCS-02] MUST:** Use a consistent Docstring format (e.g., Google or Sphinx style) containing full descriptions, arguments, and return values for all functions.
**EXCEPTION:** Internal functions (prefixed with a single underscore `_`) are exempt from the full format requirement and may use a simple one-line summary docstring instead.

## 3. Error Handling [PY-ERR]
- **[PY-ERR-01] NEVER:** Never use bare `except:` clauses. Always catch specific exceptions.

```python
# BAD [PY-ERR-01, CORE-FLOW-01]
def process_discount(price):
    try:
        if price >= 0:
            return price * 0.9
    except:
        pass # Silent error

# GOOD [PY-ERR-01, CORE-FLOW-01]
def process_discount(price: float) -> float:
    if price < 0:
        raise ValueError("Item prices cannot be negative.")
    return price * 0.9
```

## 4. Module Structure and Encapsulation [PY-MOD]
- **[PY-MOD-01] MUST:** Modules must expose a clear and concise public API. Unless a task is trivial, complex operations should be exposed via public "orchestrator" functions that delegate the actual logic to smaller sub-functions.
- **[PY-MOD-02] MUST:** Hide internal state. Prefix private/internal functions and variables with a single underscore `_`.
- **[PY-MOD-03] SHOULD:** Adhere to the "Flat is better than nested" Pythonic principle. Avoid over-engineering, deeply nested class hierarchies, or creating excessive micro-modules for tiny functions. Prefer plain functions over classes unless you need to maintain internal state.