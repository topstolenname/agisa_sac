# Pull Request

## Description

Brief description of changes...

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing

- [ ] Tests pass locally
- [ ] New tests added (if applicable)
- [ ] Documentation updated (if applicable)

## Documentation Changes

**If this PR modifies documentation in `docs/concord/`:**

- [ ] I have read [Documentation Contributing Guide](docs/CONTRIBUTING_DOCS.md)
- [ ] I have placed content in the correct location:
  - Normative principles → `docs/CONCORD.md`
  - Implementation approaches → `docs/concord/implementations/`
- [ ] I have used appropriate language:
  - Normative: "must", "shall", "is illegitimate"
  - Exploratory: "one approach", "experiment", "illustrative"
- [ ] I have NOT created authority ambiguity (mixing normative and exploratory)
- [ ] If adding implementation: I included non-normative headers
- [ ] If adding implementation: I do NOT claim these are Concord requirements
- [ ] Documentation builds successfully: `mkdocs build --strict`

**Key Question:** Would a system violating this still be Concord-compliant?
- If NO → This is normative (should be in CONCORD.md)
- If YES → This is exploratory (should be in implementations/)

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Dependent changes merged

## Additional Context

Add any other context about the PR here.
