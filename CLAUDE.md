## Github Operations
for github operations, you  must not push or commit to the upstream repository.

## Key Principle:
**Do the simplest thing that could possibly work**
No complex patterns, no over-engineered abstractions, no shadow mode, Just implement the simplest code.

## Python Execution (⚠️ CRITICAL)
```bash
# ALWAYS use uv for Python operations
uv run python <script>        # Run Python scripts
uv add <package>              # Install dependencies
uv sync                       # Sync dependencies from pyproject.toml
uv run pytest                 # Run tests

# NEVER use these directly:
python, pip, pytest           # ❌ WRONG - will cause environment issues
```

## **Serena Tools** (Primary for Code Analysis & Refactoring)
- `mcp__serena__find_symbol`: Find specific functions/classes quickly
- `mcp__serena__get_symbols_overview`: Understand file structure at a glance
- `mcp__serena__find_referencing_symbols`: Track dependencies before refactoring
- `mcp__serena__replace_symbol_body`: Replace entire functions/classes cleanly
- `mcp__serena__search_for_pattern`: Find patterns across codebase
- `mcp__serena__write_memory`: Store refactoring progress and decisions