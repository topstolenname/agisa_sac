## Workflow Patterns

### Python CLI Pattern (typical 3–5 components)

Recommended components:

1. **core-logic** - pure functions/classes for business rules
2. **storage-layer** - persistence (optional)
3. **cli-interface** - argparse / click wiring
4. **integration** - glue + main entrypoint

Testing focus:

- Core logic: unit tests, edge cases, deterministic behavior
- CLI: argument parsing + exit codes (subprocess tests are fine)

### Library/Package Pattern (typical 4–8 components)

Recommended components:

- public-api
- validation
- adapters (filesystem/http/db)
- serialization
- integration

Testing focus:

- Stable public API contracts
- Compatibility edge cases and error messages

