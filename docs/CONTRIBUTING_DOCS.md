# Contributing to Concord Documentation

## Documentation Structure

The Concord documentation maintains a strict hierarchy to prevent authority ambiguity:

```
docs/
├── CONCORD.md                          # NORMATIVE - Authoritative principles
└── concord/
    └── implementations/                # NON-NORMATIVE - Exploratory approaches
        ├── README.md                   # Framing document
        └── agisa-sac-2024/            # One implementation example
```

## Rules for Adding Documentation

### Adding to CONCORD.md (Normative)

**Only add content that:**
- Defines what legitimacy IS (not how to achieve it)
- Binds ALL compliant systems without exception
- Would make a system illegitimate if violated
- Uses authoritative language: "must", "shall", "is illegitimate"

**Examples of normative content:**
- "Illegitimate actions are inadmissible, not low-scoring"
- "Humans are co-constituents of legitimacy, not sovereign gods"
- "Systems must provide auditable external records"

### Adding to implementations/ (Exploratory)

**Add content that:**
- Describes ONE way to implement Concord principles
- Could be done differently while still being legitimate
- Uses mechanism-specific vocabulary (circuits, CMNI, etc.)
- Uses exploratory language: "one approach", "experiment", "illustrative"

**Examples of exploratory content:**
- "Mirror neuron circuits as coordination mechanisms"
- "CMNI as a proxy for coordination capacity"
- "Non-Coercion Guardian operationalizes Principles 1, 5, 6"

## Decision Tree

Use this to determine where new documentation belongs:

```
Does this content define what ALL legitimate systems must do?
├─ YES → Add to CONCORD.md
└─ NO → Does it describe how ONE system might implement Concord?
    ├─ YES → Add to implementations/<your-implementation>/
    └─ NO → Probably doesn't belong in Concord docs
```

## Creating a New Implementation

To document a new implementation approach:

1. **Create new directory:**
   ```bash
   mkdir -p docs/concord/implementations/your-implementation-name/
   ```

2. **Create index.md with required headers:**
   ```markdown
   # Your Implementation Name

   ---
   **Status**: Exploratory Implementation
   **Authority**: Non-Normative
   **Normative Source**: [Concord of Coexistence](../../../CONCORD.md)
   ---

   > ⚠️ **Implementation Note**: This document describes one experimental
   > approach to operationalizing Concord principles. It is not required,
   > canonical, or authoritative. See [Implementation Explorations](../README.md)
   > for context.

   ---
   ```

3. **Update implementations/README.md:**
   Add your implementation to the list of explorations.

4. **Update mkdocs.yml:**
   Add navigation entries under "Implementations".

5. **Link from CONCORD.md:**
   Add entry in "Implementation Explorations" section.

## Language Guidelines

### In CONCORD.md (Normative)
- ✅ Use: "must", "shall", "is illegitimate", "required"
- ❌ Avoid: "might", "could", "one approach", "example"
- ✅ Generic: "external legibility", "procedural integrity"
- ❌ Specific: "mirror neurons", "CMNI", "Article III"

### In implementations/ (Exploratory)
- ✅ Use: "one approach", "experiment", "illustrative", "explores"
- ❌ Avoid: "must", "required", "canonical"
- ✅ Specific: Name your mechanisms (circuits, metrics, etc.)
- ❌ Claim: Never say these are "required by the Concord"

## Forbidden Patterns

❌ **NEVER do these:**

1. **Claim implementations are normative:**
   - Bad: "The Concord requires mirror neuron circuits"
   - Good: "This implementation uses mirror neuron circuits"

2. **Create new 'Articles' in implementations:**
   - Bad: "Article X: New Requirement"
   - Good: "Component X: Explores Principles 2, 4"

3. **Mix normative and exploratory in same document:**
   - Each document is EITHER normative OR exploratory, never both

4. **Reference implementation details from CONCORD.md:**
   - CONCORD.md should never mention CMNI, circuits, Articles, etc.
   - It should only link to implementations/ generically

## Review Checklist

Before submitting documentation changes:

- [ ] I have identified whether this is normative or exploratory
- [ ] I have placed the content in the correct location
- [ ] I have used appropriate language (must vs. might)
- [ ] I have NOT created authority ambiguity
- [ ] If exploratory: I have added non-normative headers
- [ ] If exploratory: I do NOT claim these are Concord requirements
- [ ] Links point to correct locations
- [ ] MkDocs navigation updated (if needed)
- [ ] Documentation builds successfully: `mkdocs build --strict`

## Questions?

If unsure where documentation belongs, ask:

> "Would a system violating this still be Concord-compliant?"

- If **NO** → Normative (CONCORD.md)
- If **YES** → Exploratory (implementations/)

---

**Key Principle:** The Concord defines legitimacy. Implementations explore how
legitimacy might be realized—and are allowed to be wrong.
