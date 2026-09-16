# Secret Location Verification Drill

A standalone security and execution drill demonstrating credential availability across execution environments, illustrating why a gitignored `.env` file does not exist in fresh clones and how runtime environment variables supply credentials securely without value leakage.

---

## Mechanical Explanation

### Failure Path: Why Local `.env` is Unavailable

```text
Local .env
    ↓
.gitignore
    ↓
Git does not track .env
    ↓
Fresh clone
    ↓
.env does not exist
    ↓
Credential unavailable
```

### Success Path: Runtime Environment Variable Configuration

```text
Environment-variable configuration
    ↓
Runtime receives DRILL_SECRET_TOKEN
    ↓
/loop
    ↓
Credential detected
    ↓
PASS
```

### The Mechanism of `.gitignore`

A critical architectural distinction is that `.gitignore` does **not** delete or wipe a local `.env` file. Rather, `.gitignore` instructs Git to exclude the file from tracking and commits. 

Because Git does not track `.env`:
1. When repository code is committed and pushed, `.env` remains solely on the local filesystem.
2. When a fresh clone is provisioned or code is pulled in a new environment, `.env` does not exist in the working directory.
3. Applications or routines relying on runtime execution will fail to discover credentials unless they are injected as environment variables directly in the runtime.

When credentials are configured as runtime environment variables, the execution runtime receives `DRILL_SECRET_TOKEN` into `os.environ` upon invocation, allowing `/loop` to detect availability without reading or creating any disk files.

---

## Required Commands

The drill provides three explicit control commands:

| Command | Purpose | Behavior & Guardrails |
| :--- | :--- | :--- |
| `/goal` | Defines & displays drill objective | Sets or displays the active objective stored in `progress/goal.md`. |
| `/schedule` | Creates one-off schedule | Stores execution time in `config/schedule.json`. **Rejects recurring patterns** (e.g. `every`, `daily`, `cron`). |
| `/loop` | Executes verification routine | Performs one-off credential verification, logs progress, preserves evidence, and exits. Never leaks secret values. |

### Command Syntax

```bash
# Set or inspect objective
python main.py /goal Verify that the required secret is available from the runtime environment without exposing its value.
python main.py /goal

# Create or inspect one-off schedule
python main.py /schedule tomorrow at 9am
python main.py /schedule

# Execute single verification routine
python main.py /loop
```

Interactive mode is also available:
```bash
python main.py
drill> /goal
drill> /schedule tomorrow at 9am
drill> /loop
```

---

## Execution Flow

```text
/goal
   ↓
Define objective
   ↓
/schedule
   ↓
Create one-off execution
   ↓
/loop
   ↓
Run verification
   ↓
Record transcript/evidence
```

---

## Project Structure

```text
.
├── README.md                          # Mechanical and architectural drill documentation
├── main.py                            # Control script implementing /goal, /schedule, /loop
├── prompt.md                          # Active routine execution instructions
├── .gitignore                         # Excludes .env and cache directories from tracking
├── .env                               # Local dummy secret file (gitignored, untracked)
├── requirements.txt                   # Dependency manifest (standard library only)
├── config/
│   └── schedule.json                  # Stores one-off execution schedule state
├── progress/
│   ├── goal.md                        # Current verification goal
│   └── progress.md                    # Cumulative log of drill executions
├── evidence/
│   ├── first-run.md                   # Detailed evidence of initial run failure
│   ├── second-run.md                  # Detailed evidence of second run success
│   └── verification.md                # Comparative verification analysis
└── transcripts/
    ├── first-run-transcript.md        # Verbatim transcript of first run
    └── second-run-transcript.md       # Verbatim transcript of second run
```

---

## Security Requirements

- **Dummy Values Only:** Only synthetic dummy tokens (e.g., non-production mock credentials) are used during drills.
- **No Token Exposure:** The token value is never printed to stdout, written to logs, stored in markdown documentation, or committed to Git.
- **Safe Output Standard:**
  ```text
  PASS: DRILL_SECRET_TOKEN is available from the runtime environment.
  ```
  or
  ```text
  FAIL: DRILL_SECRET_TOKEN is not available in the runtime environment.
  ```

---

## Git Verification Commands

To confirm repository hygiene and ensure `.env` is properly ignored and untracked:

```powershell
# Verify repository status
git status

# Confirm .env is explicitly matched by .gitignore
git check-ignore -v .env

# Verify that .env is NOT tracked by Git (should return empty)
git ls-files .env
```
