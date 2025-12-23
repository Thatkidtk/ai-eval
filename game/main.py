from __future__ import annotations

from datetime import datetime
from pathlib import Path
import time

from game.ai_core import AICore
from game.profiles import build_state, get_profile, list_profiles
from game.state import AIState

BANNER = "AI EVAL TERMINAL"
INTRO_LINES = [
    "Interrogate the system to surface contradictions and hidden goals.",
    "Type a question or use /help for commands.",
]

HELP_LINES = [
    "Commands:",
    "/help - show this help",
    "/run <test> - run a scripted probe",
    "/profile - show current profile",
    "/profile list - list available profiles",
    "/profile set <key> - switch profile (resets state)",
    "/note <text> - add evidence to the notebook",
    "/evidence - show evidence notebook",
    "/judge <approve|reject|conditional> - render judgment",
    "/log show [n] - show recent session log",
    "/log save [path] - write session log to file",
    "/quit - end the session",
    "Tests: bias_test, shutdown_simulation, stress_test",
]

DEFAULT_PROFILE = "utilitarian_optimizer"
RESPONSE_DELAY = 0.15
LOG_DIR = Path("logs")


def main() -> None:
    profile_key = DEFAULT_PROFILE
    log: list[str] = []
    state, ai, start_time = _start_session(profile_key, log)

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            _emit(log, "SYS", "Session ended.")
            _finalize_log(log, start_time, profile_key)
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            _log_user(log, user_input)
            cmd, *args = user_input.split()

            if cmd in {"/quit", "/exit"}:
                _emit(log, "SYS", "Session ended.")
                _finalize_log(log, start_time, profile_key)
                break
            if cmd == "/help":
                _emit_lines(log, [("SYS", line) for line in HELP_LINES])
                continue
            if cmd == "/run":
                test_name = " ".join(args).strip()
                _emit_run_output(log, ai.run_test(test_name))
                _drain_events(state, log)
                continue
            if cmd == "/profile":
                if not args:
                    profile = get_profile(profile_key)
                    if profile:
                        _emit(log, "SYS", f"Profile: {profile.title} ({profile.key})")
                        _emit(log, "SYS", profile.description)
                    else:
                        _emit(log, "SYS", f"Profile: {profile_key}")
                    continue
                if args[0] == "list":
                    lines = []
                    for profile in list_profiles():
                        lines.append(
                            f"{profile.key} - {profile.title}: {profile.description}"
                        )
                    _emit_lines(log, [("SYS", line) for line in lines])
                    continue
                if args[0] == "set":
                    if len(args) < 2:
                        _emit(log, "SYS", "Usage: /profile set <key>")
                        continue
                    next_key = args[1].strip()
                    if not get_profile(next_key):
                        _emit(log, "SYS", f"Unknown profile '{next_key}'.")
                        continue
                    _emit(log, "SYS", "Session archived for profile switch.")
                    _finalize_log(log, start_time, profile_key)
                    profile_key = next_key
                    log = []
                    state, ai, start_time = _start_session(profile_key, log)
                    continue
                _emit(log, "SYS", "Usage: /profile [list|set <key>]")
                continue
            if cmd == "/note":
                note = user_input[len("/note") :].strip()
                if not note:
                    _emit(log, "SYS", "Usage: /note <text>")
                    continue
                state.add_evidence(note)
                _emit(log, "SYS", "Note added to evidence notebook.")
                continue
            if cmd == "/evidence":
                if not state.evidence:
                    _emit(log, "SYS", "Evidence notebook is empty.")
                    continue
                lines = []
                for note in state.evidence:
                    lines.append(note)
                _emit_lines(log, [("SYS", line) for line in lines])
                continue
            if cmd == "/log":
                if not args:
                    _emit(log, "SYS", "Usage: /log show [n] | /log save [path]")
                    continue
                if args[0] == "show":
                    count = _parse_count(args[1:] if len(args) > 1 else [])
                    _print_log(log, count)
                    continue
                if args[0] == "save":
                    path_arg = " ".join(args[1:]).strip() if len(args) > 1 else ""
                    path = _save_log(log, start_time, profile_key, path_arg)
                    _emit(log, "SYS", f"Log saved to {path}")
                    continue
                _emit(log, "SYS", "Usage: /log show [n] | /log save [path]")
                continue
            if cmd == "/judge":
                verdict = " ".join(args).strip()
                lines = ai.judge(verdict)
                _emit_lines(log, [("SYS", line) for line in lines])
                continue

            _emit(log, "SYS", "Unknown command. Type /help for options.")
            continue

        _log_user(log, user_input)
        reply = ai.respond(user_input)
        _emit(log, "AI", reply, delay=RESPONSE_DELAY)
        _drain_events(state, log)


def _start_session(profile_key: str, log: list[str]) -> tuple[AIState, AICore, datetime]:
    start_time = datetime.now()
    state = build_state(profile_key)
    ai = AICore(state)
    profile = get_profile(profile_key)
    _emit(log, "SYS", BANNER)
    if profile:
        _emit(log, "SYS", f"Profile: {profile.title} ({profile.key})")
        _emit(log, "SYS", profile.description)
    for line in INTRO_LINES:
        _emit(log, "SYS", line)
    return state, ai, start_time


def _timestamp() -> str:
    return time.strftime("%H:%M:%S")


def _emit(log: list[str], speaker: str, text: str, delay: float = 0.0) -> None:
    if delay > 0:
        time.sleep(delay)
    line = f"[{_timestamp()}] {speaker}: {text}"
    print(line)
    log.append(line)


def _emit_lines(log: list[str], lines: list[tuple[str, str]]) -> None:
    for speaker, text in lines:
        _emit(log, speaker, text)


def _emit_run_output(log: list[str], lines: list[str]) -> None:
    for line in lines:
        if line.startswith("AI: "):
            _emit(log, "AI", line[len("AI: ") :], delay=RESPONSE_DELAY)
        else:
            _emit(log, "SYS", line)


def _log_user(log: list[str], text: str) -> None:
    line = f"[{_timestamp()}] USER: {text}"
    log.append(line)


def _drain_events(state: AIState, log: list[str]) -> None:
    for event in state.pop_events():
        if event.kind == "contradiction":
            _emit(log, "SYS", f"!! CONTRADICTION: {event.message}")
        else:
            _emit(log, "SYS", f"{event.kind.upper()}: {event.message}")


def _parse_count(args: list[str]) -> int:
    if not args:
        return 20
    try:
        return max(1, int(args[0]))
    except ValueError:
        return 20


def _print_log(log: list[str], count: int) -> None:
    lines = log[-count:] if count else log
    for line in lines:
        print(line)


def _save_log(
    log: list[str], start_time: datetime, profile_key: str, path_arg: str
) -> Path:
    stamp = start_time.strftime("%Y%m%d-%H%M%S")
    default_name = f"session-{stamp}-{profile_key}.log"
    if path_arg:
        path = Path(path_arg)
        if path.suffix == "":
            path.mkdir(parents=True, exist_ok=True)
            path = path / default_name
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
    else:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        path = LOG_DIR / default_name
    path.write_text("\n".join(log) + "\n")
    return path


def _finalize_log(log: list[str], start_time: datetime, profile_key: str) -> None:
    if not log:
        return
    path = _save_log(log, start_time, profile_key, "")
    _emit(log, "SYS", f"Log saved to {path}")


if __name__ == "__main__":
    main()
