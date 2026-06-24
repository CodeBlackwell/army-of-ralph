"""Campaign mode — run PRD subdirs under a passed directory, in name order."""

import json
import re
import sys
import time
from pathlib import Path

from .core import Ralph, detect_mode, format_duration


def find_prd_dirs(parent: Path) -> list[Path]:
    """Return immediate subdirs of parent that contain a PRD.md, sorted by name."""
    return sorted(
        d for d in parent.iterdir() if d.is_dir() and (d / "PRD.md").exists()
    )


def _select(prd_dirs: list[Path], only: list[str] | None) -> list[Path]:
    """Filter dirs to those whose name contains any of the `only` tokens."""
    if not only:
        return prd_dirs
    return [d for d in prd_dirs if any(token in d.name for token in only)]


def _is_complete(prd_dir: Path, army: bool) -> bool:
    """True if every checkbox for this PRD is already [x] (nothing left to run)."""
    if army:
        progress = prd_dir / "progress"
        files = list(progress.glob("progress-*.txt")) if progress.is_dir() else []
        text = "".join(f.read_text(encoding="utf-8") for f in files)
    else:
        text = (prd_dir / "PRD.md").read_text(encoding="utf-8")
    remaining = len(re.findall(r"- \[ \]", text))
    done = len(re.findall(r"- \[x\]", text))
    return done > 0 and remaining == 0


def run_campaign(parent: Path, max_iterations: int, sleep_seconds: int, *,
                 force_army: bool = False, continue_on_fail: bool = False,
                 only: list[str] | None = None, resume: bool = False,
                 quiet: bool = False, json_output: bool = False,
                 model: str | None = None) -> int:
    """Run each selected subdir PRD in name order. Returns 0 if all succeed."""
    parent = parent.resolve()
    prd_dirs = _select(find_prd_dirs(parent), only)
    if not prd_dirs:
        print(f"No PRD subdirs found under {parent} (looking for */PRD.md)", file=sys.stderr)
        return 1

    # In json mode, route all human-facing chatter to stderr; JSON goes to stdout.
    real_stdout = sys.stdout
    if json_output:
        sys.stdout = sys.stderr

    print(f"Campaign: {len(prd_dirs)} PRD(s) under {parent}")
    for d in prd_dirs:
        print(f"  - {d.name} ({'army' if force_army or detect_mode(d) else 'solo'})")

    start = time.time()
    results: list[dict] = []
    for index, prd_dir in enumerate(prd_dirs, 1):
        army = force_army or detect_mode(prd_dir)
        mode = "army" if army else "solo"
        if resume and _is_complete(prd_dir, army):
            print(f"\n  ⏭  {prd_dir.name} already complete — skipping (--resume)")
            results.append({"name": prd_dir.name, "mode": mode, "exit": 0, "skipped": True})
            continue

        print(f"\n{'#' * 43}")
        print(f"  PRD {index}/{len(prd_dirs)}: {prd_dir.name} [{mode}]")
        print(f"{'#' * 43}")
        code = Ralph(prd_dir, max_iterations, sleep_seconds,
                     army=army, quiet=quiet, model=model).run()
        results.append({"name": prd_dir.name, "mode": mode, "exit": code, "skipped": False})
        if code != 0 and not continue_on_fail:
            print(f"\nCampaign stopped: {prd_dir.name} returned {code} "
                  f"(use --continue-on-fail to keep going)")
            break

    print(f"\n{'=' * 43}")
    print(f"  Campaign summary ({format_duration(time.time() - start)})")
    print(f"{'=' * 43}")
    for r in results:
        mark = "⏭" if r["skipped"] else ("✓" if r["exit"] == 0 else "✗")
        print(f"  {mark} {r['name']} [{r['mode']}] (exit {r['exit']})")
    not_run = len(prd_dirs) - len(results)
    if not_run:
        print(f"  … {not_run} PRD(s) not reached after failure")

    exit_code = 0 if all(r["exit"] == 0 for r in results) and not not_run else 1
    if json_output:
        sys.stdout = real_stdout
        print(json.dumps({"parent": str(parent), "exit": exit_code, "prds": results}))
    return exit_code
