# Workflow Patterns

This document describes common development workflows for different project types.

## Standard Workflow

All projects follow this basic flow:

```
Planning Phase
    ↓
Implementation Phase (loop per component)
    ↓
Documentation Phase
```

## Project-Specific Patterns

### CLI Tool Pattern

**Components:** (3-5 typical)
1. **core-logic** - Business logic, algorithms, data processing
2. **cli-interface** - Argument parsing, command handlers
3. **persistence** - File I/O, database operations (optional)
4. **integration** - Glue code connecting components

**Testing Focus:**
- CLI argument validation
- Command output formatting
- Error messages for invalid input
- Help text completeness

**Example:** TODO list manager, file converter, data analyzer

---

### Library/Package Pattern

**Components:** (4-8 typical)
1. **core-api** - Public interface, main classes/functions
2. **utilities** - Helper functions, validators
3. **exceptions** - Custom error types
4. **io-handlers** - File/network operations (if applicable)
5. **integration** - Bringing it all together

**Testing Focus:**
- API contract compliance
- Edge case handling
- Documentation examples work
- Version compatibility

**Example:** PDF parser, HTTP client, data validation library

---

### Web Application Pattern

**Components:** (5-10 typical)
1. **models** - Data models, database schemas
2. **routes** - HTTP endpoint handlers
3. **business-logic** - Core functionality
4. **middleware** - Auth, logging, error handling
5. **templates** - UI rendering (if server-side)
6. **static-assets** - CSS/JS (if applicable)
7. **integration** - Application setup

**Testing Focus:**
- Endpoint responses
- Authentication/authorization
- Database operations
- Error handling
- Security (CSRF, XSS, SQL injection)

**Example:** Dashboard, API service, content management system

---

### Data Processing Pipeline Pattern

**Components:** (4-7 typical)
1. **ingestion** - Data loading, parsing
2. **validation** - Schema checking, cleaning
3. **transformation** - Processing, enrichment
4. **output** - Export, visualization, storage
5. **integration** - Pipeline orchestration

**Testing Focus:**
- Data integrity through pipeline
- Error recovery
- Performance with large datasets
- Output format correctness

**Example:** ETL tool, data aggregator, report generator

---

## Component Size Guidelines

**Too Small:** (<50 lines)
- May indicate over-fragmentation
- Consider merging with related component

**Good Size:** (50-300 lines)
- Easy to understand and test
- Single responsibility
- Manageable scope

**Too Large:** (>500 lines)
- Consider splitting into sub-components
- Look for separate concerns

---

## Iteration Guidelines

### When to Kick Back to Developer

QA should fail the component if:
- Tests reveal logical errors
- Edge cases cause crashes
- Security vulnerabilities found
- Code doesn't match spec requirements

### When to Advance

Advance to next component when:
- All tests pass
- Code meets quality standards
- Edge cases handled
- No obvious security issues

### Maximum Iterations

If a component fails QA more than 3 times:
1. Stop and review the spec
2. Check if component scope is too large
3. Consider redesigning the component
4. Re-engage Architect if needed

---

## Special Considerations

### Database-Heavy Projects

Add extra components:
- **schema-migrations** - Database version control
- **data-access-layer** - ORM or query builder
- **seed-data** - Test data generation

### API Integrations

Add extra components:
- **api-client** - External service communication
- **response-handlers** - Parsing, error handling
- **rate-limiter** - Prevent API abuse

### Performance-Critical

Add benchmarking phase:
- **profiling** - Identify bottlenecks
- **optimization** - Improve slow components
- **load-testing** - Verify under stress

---

## Workflow Customization

The orchestrator supports custom workflows. To adapt:

1. **Modify component list** in `design.md`
2. **Adjust QA criteria** in agent-personas.md
3. **Add custom checks** in orchestrator.py

Example: Adding a "Security Audit" phase between QA and Documentation.
