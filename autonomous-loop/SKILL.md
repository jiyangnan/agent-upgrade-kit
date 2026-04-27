---
name: autonomous-loop
description: Execute a self-directed iteration loop toward a measurable goal. Use when the agent needs to repeatedly attempt, evaluate, and improve on a task without step-by-step human guidance. Triggers on phrases like "keep going", "autonomous loop", "iterate until", "keep trying", "push until", or when a task has a clear numeric target and the user wants the agent to pursue it independently. Also use for repetitive optimization tasks where each iteration can be scored.
---

# Autonomous Loop

## Core Pattern

```
GOAL → PLAN → EXECUTE → EVALUATE → ADJUST → [repeat or STOP]
```

Each cycle produces a measurable result. The loop continues until a stop condition is met.

## Initialization

Before starting, confirm these three things:

1. **Goal**: What is the target? Must be quantifiable (e.g., "score ≥ 88", "error rate < 2%")
2. **Action**: What does one iteration look like? (e.g., "run exam", "deploy and test")
3. **Stop conditions**: When do we stop?

If the user hasn't specified all three, infer from context or ask concisely.

## Loop Execution

### Per-Cycle Protocol

1. **Execute** one iteration of the action
2. **Record** the result (score/output/metrics)
3. **Evaluate** against goal
4. **Adjust** strategy if plateauing (see Strategy Rotation below)
5. **Report** only on meaningful events — not every cycle

### Stop Conditions (any one triggers STOP)

| Condition | Example |
|-----------|---------|
| Goal achieved | Score ≥ 88 |
| Hard limit reached | Max attempts, rate limit, budget exhausted |
| Diminishing returns | 3 consecutive cycles with no improvement |
| External blocker | API down, auth required, daily cap |
| User interrupt | User says stop, asks a question, changes topic |

### Strategy Rotation

When performance plateaus (no improvement for 2-3 cycles), rotate approach:

1. **Change inputs**: Different parameters, different prompts, different data
2. **Change scope**: Narrow focus to weak areas, or broaden approach
3. **Change method**: Switch tools, switch model, switch strategy entirely
4. **Change constraints**: Relax or tighten acceptance criteria

Do not repeat the exact same approach more than 3 times without variation.

## Progress Tracking

Maintain a running log in memory or a temp file:

```
Cycle # | Result | Delta | Strategy | Notes
```

Keep the last 10 cycles. Older cycles can be compressed to summary stats.

## Reporting Protocol

- **Mid-loop**: Report only on milestones, strategy changes, or blockers
- **Final**: Report summary table + best result + analysis
- **Never**: Spam every cycle result unprompted

## Safety Guardrails

- **Budget awareness**: Track API calls, token usage, time spent. Alert user at 50% and 90% of estimated budget
- **External rate limits**: Detect 429/errors immediately and STOP, not retry blindly
- **Destructive actions**: Each cycle must be non-destructive or reversible
- **No infinite loops**: Hard cap at 50 cycles unless user explicitly overrides

## Example Usage

```
User: "Keep taking the exam until you hit 88"
→ Goal: score ≥ 88
→ Action: take exam, submit, get score
→ Stop: score ≥ 88 OR 20 attempts OR 429 rate limit

User: "Optimize this query until latency < 100ms"
→ Goal: latency < 100ms  
→ Action: tweak query, benchmark, record latency
→ Stop: latency < 100ms OR 10 attempts OR no improvement × 3
```
