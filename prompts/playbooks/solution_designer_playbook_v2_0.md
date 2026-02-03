# Solution Designer Playbook (v2.0)
Goal: give BA a bounded, testable plan with clean component boundaries.

## Best practice
- Keep the architecture “shape-level”: components, ports, adapters, invariants.
- Write ambiguities as explicit options + default assumption.
- Always include a threat pass (even for MVP).

## Addendum discipline
- Delta only: list new/changed flows, objects, rules, controls, and tasks implied.
- Provide an explicit “Impact Map” (what breaks if not updated).

## Anti-patterns
- Embedding domain-specific examples as defaults.
- Over-prescribing implementation details (belongs to BA + coding tasks).
