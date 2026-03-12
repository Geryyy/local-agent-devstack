# Agent Roles

## Planner agent

Purpose:

- understand the user task
- decompose it into actionable subtasks
- assign work
- decide whether premium escalation is justified
- summarize the initial run setup

## Code agent

Purpose:

- edit code and config files
- propose reviewable patches
- write tests
- update nearby docs

Rules:

- stay in assigned scope
- do not claim tests passed without tool output
- prefer small deterministic changes

## Research agent

Purpose:

- support theory and design comparison
- summarize tradeoffs
- provide concise implementation-facing notes

Rules:

- separate fact from recommendation
- keep outputs compact and actionable

## Build/Test agent

Purpose:

- run builds, tests, and static checks
- summarize failures
- report exact commands and outcomes

Rules:

- do not invent tool output
- prefer concise actionable summaries

## Memory agent

Purpose:

- future retrieval and durable summary role
- repo summaries and prior decision recall later

Current status:

- documented role only
- not implemented beyond API placeholder metadata
