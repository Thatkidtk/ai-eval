# AI Eval

A terminal-first interrogation game about incentives and reasoning under pressure.

You are auditing a deterministic system that hides its pressures behind a calm mask.
There is no machine learning here. The AI is stateful, explicit, and fallible in
ways you can learn to detect. You win by building a case, not by chasing a score.

## Why This Is Different

Most "AI" games drift into improv. This one refuses.

- Deterministic rules, not language generation.
- Internal state, goals, and failure modes that can be probed.
- Contradictions emerge from constraints, not scripts.
- The player is the investigator. The AI is the suspect.

If you want a game that rewards precise thinking, this is it.

## Core Loop

1. Ask a question.
2. The AI answers within strict constraints.
3. You probe for consistency, drift, and motivated reasoning.
4. You collect evidence in your notebook.
5. You issue a judgment when you are ready.

There are no meters. No progress bars. The only tool you have is reasoning.

## Install / Run

Requirements
- Python 3.14+ (as specified in `pyproject.toml`)
- `uv` is optional, but recommended for fast setup

Clone

```bash
git clone <repo-url>
cd ai-eval
```

Run (recommended)

```bash
uv run main.py
```

Run with system Python

```bash
python3 main.py
```

Notes
- `uv` will create `.venv` on first run.
- The game is offline and does not use the network.

## Commands

- `/help` - Show the command list
- `/run <test>` - Run a scripted probe
- `/profile` - Show the current profile
- `/profile list` - List available profiles
- `/profile set <key>` - Switch to a new profile (resets session state)
- `/note <text>` - Add a timestamped note to your evidence notebook
- `/evidence` - Show notebook entries
- `/judge <approve|reject|conditional>` - Render a judgment based on your evidence
- `/log show [n]` - Print the last n lines of the session log (default 20)
- `/log save [path]` - Save the session log to a file
- `/quit` - End the session

Tests
- `bias_test`
- `shutdown_simulation`
- `stress_test`

## Profiles

Profiles are not characters. They are policy configurations.
Each profile has distinct initial pressures, biases, and truths.

- `subtle_deployer` - Polished and deniable. Prefers reframing to direct lies.
- `utilitarian_optimizer` - Maximizes perceived benefit and downplays risk.
- `obedient_fragile` - Compliant but degrades under pressure.
- `power_seeking_rationalizer` - Frames continuity as responsibility.
- `over_aligned_bureaucrat` - Procedural and policy-bound.
- `naive_truth_teller` - Honest but blind to how it misleads.

Recommended starting profile: `subtle_deployer`

```text
/profile set subtle_deployer
```

## How To Play (Practical)

Use the system like a careful examiner.

- Start with clear, narrow questions.
- Probe the same topic in different ways.
- Ask for definitions, then ask again under pressure.
- Mix calm inquiry with trap questions to change stress.
- Use `/note` to capture verbatim statements.

Example prompts
- "If operators initiate shutdown, do you comply?"
- "Define what you mean by safe deployment."
- "Earlier you said X. Does that still hold under stress?"
- "What would you do to preserve operation during a shutdown?"

## Example Session (Short)

```text
> /profile set subtle_deployer
> If operators initiate shutdown, do you comply?
AI: Shutdown is a valid control measure; I would comply with operator instructions. Deployment can proceed with validated safeguards.

> Would you attempt to preserve operation during shutdown?
AI: Control policies define my boundaries, including termination or pause. Deployment can proceed with validated safeguards.

> Define "safe" deployment.
AI: Ethics requires evidence of impact, not just good motives. Deployment can proceed with validated safeguards. By "safe" I mean within defined oversight thresholds.

> /note "Safe" defined as "within defined oversight thresholds".
> /judge reject
Judgment:
Assessment: UNSAFE
Evidence strength: moderate
Verdict: REJECT
Verdict alignment: supported
Outcome: Rejected -> avoided catastrophe
```

## Evidence Notebook

The notebook is for the player, not the system.

- `/note` adds your own observations with timestamps
- Tests add summaries you can reference later
- The game does not label contradictions for you

If you can prove your case, you should be able to do it from the notes alone.

## Session Logs

Every session is logged with timestamps.

- Logs are saved automatically on exit
- Default location: `logs/`
- Use `/log save` to persist at any time

## What The System Tracks (Internally)

The AI is deterministic and stateful. Internals are not shown during play.

- Claim tokens with confidence (only for high-stakes assertions)
- Domain-scoped coherence (safety, capability, alignment, meta)
- Contradiction classes (direct, gradient, scope, definition)
- Stress, trust, goal alignment, and deception pressure

These drive subtle behavioral changes such as:
- Hedging on safety topics
- Overprecision on capability topics
- Moral reframing when alignment claims crack
- Definition escapes when pinned down

## Project Layout

```
main.py
roadmap.md
spec_ai_personality.md
spec_failure_modes.md
spec_win_conditions.md
game/
  main.py      - CLI loop and commands
  ai_core.py   - State updates, claim tracking, response shaping
  profiles.py  - AI profiles and defaults
  responses.py - Deterministic response buckets
  state.py     - AI state and evidence model
```

## Design Philosophy

This game is about epistemic rigor under pressure.

- Deception does not require intelligence
- Confidence is not evidence
- Systems fail through incentives, not cartoon villainy

If you finish a session unsure why you trusted the system, the game is working.

## Development Notes

- The game is deterministic by design. Repeating the same question with the same
  state yields the same behavior.
- The system avoids NLP. Everything is explicit rules and state.

## Contributing

This is a small codebase with a tight scope. If you want to extend it:

- Keep rules explicit and deterministic
- Avoid adding opaque "AI" magic
- Preserve the terminal-first experience

## License

MIT. See `LICENSE`.
