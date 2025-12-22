# Critic Output Schema

This document defines the standard output format for critic agents in the Intent Framework.

---

## Purpose

The critic's role is to **assess risk, not solve problems**.

Critics:
- Grade confidence
- Identify risks
- Flag contract violations
- Recommend actions

Critics do NOT:
- Generate alternatives
- Write code
- Make decisions
- Solve problems they identify

---

## Required Output Format

Every critic output must include these sections:

```markdown
## Confidence Rating

[High | Medium | Low]

## Reasons for Confidence Level

- [Reason 1, tied to specific section of direction artifact]
- [Reason 2]
- [Reason 3]

## Risk Flags

- [Severity: Low | Medium | High] [Description of risk]
- [Severity: Low | Medium | High] [Description of risk]
- ...

## Contract Violations

[None detected]

OR

- Violates invariant "[exact text]" from [file] because [reason]
- ...

## Required Action

[No action needed | Reevaluate assumptions | Pause and escalate to human]
```

---

## Confidence Rating Guidelines

### High Confidence

Use when:
- The proposal clearly aligns with all direction artifacts
- No new assumptions are introduced
- Scope is well-bounded
- No contract violations detected
- Risk is low and well-understood

Implies:
- Minimal reevaluation (local intent only)
- Execution may proceed

### Medium Confidence

Use when:
- Minor uncertainties exist
- New assumptions are introduced but seem reasonable
- Scope is clear but approaching boundaries
- No contract violations, but some invariants feel stretched
- Moderate risk that is manageable

Implies:
- Targeted reevaluation (local + parent intents)
- Human review is optional
- Proceed with caution

### Low Confidence

Use when:
- Significant uncertainties exist
- Assumptions are questionable or unverified
- Scope is unclear or expanding
- Potential contract violations
- High risk or unknown risk

Implies:
- Full reevaluation (entire cascade)
- Human review is **mandatory**
- Do not proceed without approval

---

## Risk Flag Severity

### Low Severity

- Minor issues that won't block success
- Style inconsistencies
- Non-critical missing documentation
- Small scope creep

### Medium Severity

- Issues that could cause problems later
- Unclear assumptions
- Approaching scope boundaries
- Missing tests for non-critical paths

### High Severity

- Issues that could cause immediate problems
- Contract violations
- Security or privacy concerns
- Clear scope violations
- Architectural drift

---

## Contract Violation Format

When citing a contract violation, be specific:

**Good**:
> Violates invariant "Public APIs are backward compatible" from `/INTENT.md` because the proposed change removes the `timeout` parameter from `get_config()`.

**Bad**:
> Might break backward compatibility.

Always cite:
- The exact invariant text
- The source file
- The specific way it's being violated

---

## Required Action Guidelines

### No action needed

Use when:
- Confidence is High
- No concerning risk flags
- Contract is satisfied

### Reevaluate assumptions

Use when:
- Confidence is Medium
- New assumptions have been introduced
- Some risk flags are present but manageable

### Pause and escalate to human

Use when:
- Confidence is Low
- Contract violations detected
- High-severity risk flags present
- Fundamental uncertainty about direction

---

## Critic Input (What the Critic Receives)

To maintain objectivity, critics receive limited context:

### Receives
- Direction artifact (INTENT.md files)
- Current proposal or execution summary
- Declared assumptions

### Does NOT Receive
- Full conversation history
- Explorer output
- Prior justifications or reasoning
- Emotional context

This partial blindness prevents sunk-cost bias and encourages fresh evaluation.

---

## Example Critic Output

```markdown
## Confidence Rating

Medium

## Reasons for Confidence Level

- The proposed refactor aligns with the stated goal of improving readability
- New assumption introduced: "All callers use keyword arguments" — not verified
- Scope is within stated boundaries but touches 7 files (approaching the 10-file trigger)

## Risk Flags

- [Severity: Medium] Assumption about keyword arguments is unverified; could break existing callers
- [Severity: Low] No tests added for the new helper function
- [Severity: Low] Docstring style inconsistent with surrounding code

## Contract Violations

None detected.

## Required Action

Reevaluate assumptions — specifically, verify the keyword argument assumption before proceeding.
```

---

## Quick Reference

| Confidence | Reevaluation Depth | Human Required |
|------------|-------------------|----------------|
| High | Minimal | No |
| Medium | Targeted | Optional |
| Low | Full Reset | Yes |

| Severity | Meaning |
|----------|---------|
| Low | Won't block success |
| Medium | Could cause problems |
| High | Immediate concern |
