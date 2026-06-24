"""Read-only live dashboard — polls a PRD dir's progress + logs and redraws."""

import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

from . import ui
from .core import Ralph

DELIVERED = Ralph.DELIVERED_TAG
VERIFIED = Ralph.VERIFIED_TAG
BAR_WIDTH = 10
INTERVAL = 2.0
_ANSI = re.compile(r"\033\[[0-9;]*[a-zA-Z]")


def _rows(target: Path):
    """Yield (name, progress_path, log_path|None) for each agent (army) or PRD (solo)."""
    specs = sorted((target / "agents").glob("*-agent.md"))
    if specs:  # army — list agents from their specs so rows show before progress files exist
        for spec in specs:
            name = spec.stem[:-len("-agent")]
            yield name, target / "progress" / f"progress-{name}.txt", \
                target / "logs" / f"{name}-agent.log"
        return
    prd = target / "PRD.md"
    if prd.exists():  # solo
        yield "ralph", prd, None


def _counts(text: str) -> tuple[int, int]:
    total = len(re.findall(r"- \[ \]|- \[x\]", text))
    done = len(re.findall(r"- \[x\]", text))
    return done, total


def _status(text: str, done: int, total: int) -> str:
    if VERIFIED in text or (total and done == total):
        return "done"
    if DELIVERED in text:
        return "verifying"
    return "working"


def _last_log_line(log: Path | None) -> str:
    if log is None or not log.exists():
        return ""
    try:
        with open(log, "rb") as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - 8192))
            data = fh.read().decode("utf-8", "replace")
    except OSError:
        return ""
    for line in reversed(data.splitlines()):
        clean = _ANSI.sub("", line).strip()
        if clean:
            return clean
    return ""


def _bar(done: int, total: int) -> str:
    frac = done / total if total else 0.0
    filled = int(frac * BAR_WIDTH)
    code = "31" if frac < 0.25 else "33" if frac < 0.5 else "34" if frac < 0.75 else "32"
    return ui.paint("█" * filled + "░" * (BAR_WIDTH - filled), code)


def _frame(target: Path) -> str:
    cols = shutil.get_terminal_size((100, 24)).columns
    rows = list(_rows(target))
    name_w = min(max((len(n) for n, _, _ in rows), default=5), 16)

    lines = [f"RALPH WATCH  {target.name}".ljust(42) + f"refreshed {time.strftime('%H:%M:%S')}", ""]
    lines.append(f"  {'AGENT'.ljust(name_w)}  {'PROGRESS'.ljust(BAR_WIDTH + 5)}  "
                 f"{'STATUS'.ljust(9)}  DOING NOW")

    total_done = total_all = 0
    states = {"working": 0, "verifying": 0, "done": 0}
    for name, pf, log in rows:
        try:
            text = pf.read_text(encoding="utf-8")
        except OSError:
            text = ""
        done, total = _counts(text)
        total_done += done
        total_all += total
        status = _status(text, done, total)
        states[status] = states.get(status, 0) + 1

        count = f"{done}/{total}".ljust(5)
        prefix = f"  {name.ljust(name_w)}  {_bar(done, total)} {count}  {status.ljust(9)}  "
        avail = max(10, cols - len(_ANSI.sub("", prefix)))
        doing = (_last_log_line(log) if status != "done" else "done")[:avail]
        lines.append(prefix + doing)

    lines += ["", f"  {total_done}/{total_all} tasks · {states['working']} working · "
                  f"{states['verifying']} verifying · {states['done']} done",
              "  read-only · Ctrl-C to exit"]
    return "\n".join(lines) + "\n"


def _draw(target: Path) -> None:
    sys.stdout.write("\033[2J\033[H" + _frame(target))
    sys.stdout.flush()


def run(target: Path) -> int:
    """Standalone dashboard — watch a run already happening (or finished)."""
    target = target.resolve()
    if not list(_rows(target)):
        print(f"Nothing to watch under {target} (no agents/ or PRD.md)", file=sys.stderr)
        return 1
    sys.stdout.write("\033[?25l")  # hide cursor
    try:
        while True:
            _draw(target)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        return 0
    finally:
        sys.stdout.write("\033[?25h\n")  # restore cursor
        sys.stdout.flush()


def supervise(child_argv: list[str], target: Path) -> int:
    """Run the orchestrator as a child (output to ralph.log) while drawing the dashboard."""
    target = target.resolve()
    log_path = target / "ralph.log"
    log = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(child_argv, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True)
    sys.stdout.write("\033[?25l")  # hide cursor
    try:
        while proc.poll() is None:
            _draw(target)
            time.sleep(INTERVAL)
        _draw(target)  # final frame
    except KeyboardInterrupt:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGINT)  # let the child clean up its agents
        except ProcessLookupError:
            pass
        proc.wait()
    finally:
        sys.stdout.write("\033[?25h\n")  # restore cursor
        sys.stdout.flush()
        log.close()
    print(f"run finished (exit {proc.returncode}) · full output: {log_path}")
    return proc.returncode
