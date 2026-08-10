# Issue tracker: GitHub

Issues and planning artifacts for this repository live in GitHub Issues. Use the `gh` CLI and infer the repository from its Git remote.

## Conventions

- Create, read, comment on, label, assign, and close issues with `gh issue`.
- Pull requests are not a triage request surface.
- A Wayfinder map is labelled `wayfinder:map`.
- Map tickets are GitHub sub-issues labelled `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, or `wayfinder:task`.
- Use native GitHub issue dependencies for blocking relationships, falling back to `Blocked by:` references when unavailable.
- Claim a ticket by assigning it to the current developer before beginning work.
- Resolve a ticket by commenting with its answer, closing it, and adding a linked one-line decision pointer to the map.
- Refer to issues by their linked titles in human-readable output, not bare issue numbers.
