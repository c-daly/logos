# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for Project LOGOS. ADRs document significant architectural decisions made during the project, including the context, rationale, and consequences of each decision.

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences. ADRs help teams:

- Understand why certain architectural choices were made
- Avoid revisiting settled decisions
- Onboard new team members more effectively
- Document the evolution of the system architecture

## ADR Format

We follow a modified version of Michael Nygard's ADR format. See [TEMPLATE.md](TEMPLATE.md) for the standard template.

Each ADR includes:
- **Status**: Proposed, Accepted, Deprecated, or Superseded
- **Context**: The problem statement and background
- **Decision Drivers**: Forces and concerns that influenced the decision
- **Considered Options**: Alternative approaches evaluated
- **Decision Outcome**: The chosen option and justification
- **Consequences**: Positive and negative outcomes
- **References**: Links to related documentation and resources

## Naming Convention

ADR files follow this naming pattern:
```
NNNN-short-title.md
```

Where:
- `NNNN` is a zero-padded sequential number (0001, 0002, etc.)
- `short-title` is a brief, hyphenated description

Examples:
- `0001-use-neo4j-for-graph-database.md`
- `0002-use-milvus-for-vector-storage.md`

## Phase 1 ADRs

The following ADRs document foundational architectural decisions made during Phase 1:

- [ADR-0001](0001-use-neo4j-for-graph-database.md) - Use Neo4j for Graph Database
- [ADR-0002](0002-use-milvus-for-vector-storage.md) - Use Milvus for Vector Storage
- [ADR-0003](0003-shacl-for-level-1-validation.md) - SHACL for Level 1 Validation
- [ADR-0004](0004-htn-based-planning-approach.md) - HTN-based Planning Approach
- [ADR-0005](0005-vector-embedding-strategy.md) - Vector Embedding Strategy

## Creating a New ADR

1. Copy `TEMPLATE.md` to a new file with the next sequential number
2. Fill in all sections with relevant information
3. Submit for review as part of a pull request
4. Update this README to include the new ADR in the index
5. Reference the ADR in related documentation and code comments

## Relationship to Specification

ADRs complement but do not replace the main specification documents:
- **Specification** (`docs/architecture/LOGOS_SPEC.md`): Describes the current system architecture and design
- **ADRs**: Document the decision-making process and rationale behind architectural choices

When architectural decisions evolve, create a new ADR that supersedes the old one rather than modifying the original ADR.

## References

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) by Michael Nygard
- [ADR GitHub Organization](https://adr.github.io/)
