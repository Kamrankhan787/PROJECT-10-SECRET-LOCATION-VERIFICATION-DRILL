# Evidence: Verification Summary

## Comparative Run Summary

| Metric / Dimension | Run 1 (Local `.env` Only) | Run 2 (Runtime Environment Variable) |
| :--- | :--- | :--- |
| **Credential Storage** | Local `.env` file (gitignored) | Process Environment (`os.environ`) |
| **Prompt Instruction** | Baseline drill instructions | `credentials are available as environment variables; do not look for a .env file.` |
| **Runtime Detection** | Not found in `os.environ` | Successfully found in `os.environ` |
| **Verification Result** | `FAIL` | `PASS` |
| **Exit Code** | `1` | `0` |
| **Token Exposure** | None (masked / omitted) | None (masked / omitted) |
| **Execution Type** | One-off | One-off |

## Key Findings

1. **Why Local `.env` Failed in Fresh/Standard Execution:**
   The `.env` file was excluded by `.gitignore`. In a fresh clone or runtime environment, Git ignores `.env`, so the file does not exist. Furthermore, execution runtimes do not automatically import arbitrary filesystem `.env` files into environment variables without explicit tooling or injection.

2. **Why Runtime Environment Succeeded:**
   When credentials are supplied as runtime environment variables, `os.environ.get("DRILL_SECRET_TOKEN")` retrieves the token immediately upon execution without reading from untracked files or requiring disk persistence.

3. **Security Invariant:**
   Across both runs, the actual value of `DRILL_SECRET_TOKEN` was never logged to console outputs, transcripts, progress files, or version control.
