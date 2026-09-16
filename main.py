#!/usr/bin/env python3
"""
Secret Location Verification Drill
Standalone verification drill for credential availability in execution runtimes.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
PROGRESS_DIR = BASE_DIR / "progress"
EVIDENCE_DIR = BASE_DIR / "evidence"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

SCHEDULE_FILE = CONFIG_DIR / "schedule.json"
GOAL_FILE = PROGRESS_DIR / "goal.md"
PROGRESS_FILE = PROGRESS_DIR / "progress.md"
PROMPT_FILE = BASE_DIR / "prompt.md"
VERIFICATION_EVIDENCE_FILE = EVIDENCE_DIR / "verification.md"

SECRET_KEY = "DRILL_SECRET_TOKEN"


def ensure_directories():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def cmd_goal(args: str = "") -> int:
    """Defines and displays the objective of the routine."""
    ensure_directories()
    goal_text = args.strip()
    if goal_text:
        content = f"# Current Objective\n\n{goal_text}\n"
        GOAL_FILE.write_text(content, encoding="utf-8")
        print(f"Goal set: {goal_text}")
    else:
        if GOAL_FILE.exists():
            content = GOAL_FILE.read_text(encoding="utf-8").strip()
            # Extract content after header if present
            lines = [l for l in content.splitlines() if not l.startswith("#") and l.strip()]
            active_goal = "\n".join(lines).strip() if lines else content
            print(f"Current Goal: {active_goal}")
        else:
            print("No active goal set. Use '/goal <objective>' to set an objective.")
    return 0


def cmd_schedule(args: str = "") -> int:
    """Creates or displays a one-off schedule for the routine. Recurring schedules are rejected."""
    ensure_directories()
    schedule_text = args.strip()

    if not schedule_text:
        if SCHEDULE_FILE.exists():
            try:
                data = json.loads(SCHEDULE_FILE.read_text(encoding="utf-8"))
                print(f"Active Schedule: {data.get('schedule', 'None')} (Type: {data.get('type', 'one-off')})")
            except Exception:
                print("Invalid schedule configuration found.")
        else:
            print("No schedule configured. Use '/schedule <time_expression>' to schedule a one-off run.")
        return 0

    # Reject recurring schedules
    recurring_patterns = [
        r"\bevery\b",
        r"\bdaily\b",
        r"\bweekly\b",
        r"\bmonthly\b",
        r"\bhourly\b",
        r"\brecurring\b",
        r"\bcron\b",
        r"\beach\b",
    ]
    for pattern in recurring_patterns:
        if re.search(pattern, schedule_text, re.IGNORECASE):
            print(f"ERROR: Recurring schedules are forbidden in this drill. Only one-off schedules are permitted.")
            return 1

    payload = {
        "type": "one-off",
        "schedule": schedule_text,
        "recurring": False,
        "configured_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending"
    }

    SCHEDULE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"One-off schedule registered: '{schedule_text}'. Recurring execution disabled.")
    return 0


def cmd_loop() -> int:
    """
    Executes the verification routine once.
    1. Reads current goal.
    2. Executes the credential check.
    3. Records the result.
    4. Preserves evidence.
    5. Never exposes the secret.
    6. Finishes after the one-off execution.
    """
    ensure_directories()

    # 1. Read the current goal
    if GOAL_FILE.exists():
        goal_content = GOAL_FILE.read_text(encoding="utf-8").strip()
        lines = [l for l in goal_content.splitlines() if not l.startswith("#") and l.strip()]
        current_goal = "\n".join(lines).strip() if lines else goal_content
    else:
        current_goal = "Verify secret availability."

    print(f"Executing drill routine for goal: {current_goal}")

    # Inspect prompt instructions if available
    prompt_instruction = ""
    if PROMPT_FILE.exists():
        prompt_instruction = PROMPT_FILE.read_text(encoding="utf-8").strip()

    # 2. Execute credential check strictly against runtime environment variables
    secret_value = os.environ.get(SECRET_KEY)
    token_present = bool(secret_value and len(secret_value.strip()) > 0)

    timestamp = datetime.now(timezone.utc).isoformat()
    status_label = "PASS" if token_present else "FAIL"

    # 3 & 5. Safe output - NEVER output secret value
    if token_present:
        result_message = f"PASS: {SECRET_KEY} is available from the runtime environment."
    else:
        result_message = f"FAIL: {SECRET_KEY} is not available in the runtime environment."

    print(result_message)

    # 4. Record progress
    progress_entry = (
        f"## Routine Execution - {timestamp}\n"
        f"- Goal: {current_goal}\n"
        f"- Status: {status_label}\n"
        f"- Result: {result_message}\n"
        f"- Prompt Instruction: {prompt_instruction or 'None'}\n"
        f"- Execution Type: One-off\n\n"
    )

    if not PROGRESS_FILE.exists():
        PROGRESS_FILE.write_text("# Execution Progress Log\n\n" + progress_entry, encoding="utf-8")
    else:
        with PROGRESS_FILE.open("a", encoding="utf-8") as f:
            f.write(progress_entry)

    # Update schedule status if one-off execution was registered
    if SCHEDULE_FILE.exists():
        try:
            sched_data = json.loads(SCHEDULE_FILE.read_text(encoding="utf-8"))
            sched_data["status"] = f"executed ({status_label})"
            sched_data["executed_at"] = timestamp
            SCHEDULE_FILE.write_text(json.dumps(sched_data, indent=2), encoding="utf-8")
        except Exception:
            pass

    print("Routine completed. One-off execution finished.")
    return 0 if token_present else 1


def parse_and_execute(raw_input: str) -> int:
    line = raw_input.strip()
    if not line:
        return 0

    parts = line.split(maxsplit=1)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    if command == "/goal":
        return cmd_goal(args)
    elif command == "/schedule":
        return cmd_schedule(args)
    elif command == "/loop":
        return cmd_loop()
    elif command in ("/exit", "exit", "quit"):
        sys.exit(0)
    else:
        print(f"Unknown command: '{command}'. Available commands: /goal, /schedule, /loop")
        return 1


def main():
    if len(sys.argv) > 1:
        # CLI argument mode: python main.py /goal ... or python main.py /loop
        full_command = " ".join(sys.argv[1:])
        sys.exit(parse_and_execute(full_command))
    else:
        # Interactive REPL mode
        ensure_directories()
        print("Secret Location Verification Drill")
        print("Commands: /goal [objective], /schedule [expression], /loop, exit")
        try:
            while True:
                user_cmd = input("drill> ")
                parse_and_execute(user_cmd)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting drill.")
            sys.exit(0)


if __name__ == "__main__":
    main()
