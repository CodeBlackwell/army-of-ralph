"""Campaign mode — run every PRD subdir under a passed directory, in order."""

from pathlib import Path

from .core import Ralph, detect_mode, format_duration
import time


def find_prd_dirs(parent: Path) -> list[Path]:
    """Return immediate subdirs of parent that contain a PRD.md, sorted by name."""
    return sorted(
        d for d in parent.iterdir() if d.is_dir() and (d / "PRD.md").exists()
    )


def run_campaign(parent: Path, max_iterations: int, sleep_seconds: int,
                 force_army: bool = False) -> int:
    """Run each subdir PRD in name order, fail-fast. Returns 0 if all succeed."""
    parent = parent.resolve()
    prd_dirs = find_prd_dirs(parent)
    if not prd_dirs:
        print(f"No PRD subdirs found under {parent} (looking for */PRD.md)")
        return 1

    print(f"Campaign: {len(prd_dirs)} PRDs under {parent}")
    for d in prd_dirs:
        print(f"  - {d.name} ({'army' if force_army or detect_mode(d) else 'solo'})")

    start = time.time()
    results: list[tuple[str, str, int]] = []
    for index, prd_dir in enumerate(prd_dirs, 1):
        army = force_army or detect_mode(prd_dir)
        mode = "army" if army else "solo"
        print(f"\n{'#' * 43}")
        print(f"  PRD {index}/{len(prd_dirs)}: {prd_dir.name} [{mode}]")
        print(f"{'#' * 43}")
        code = Ralph(prd_dir, max_iterations, sleep_seconds, army=army).run()
        results.append((prd_dir.name, mode, code))
        if code != 0:
            print(f"\nCampaign stopped: {prd_dir.name} returned {code}")
            break

    print(f"\n{'=' * 43}")
    print(f"  Campaign summary ({format_duration(time.time() - start)})")
    print(f"{'=' * 43}")
    for name, mode, code in results:
        print(f"  {'✓' if code == 0 else '✗'} {name} [{mode}] (exit {code})")
    skipped = len(prd_dirs) - len(results)
    if skipped:
        print(f"  … {skipped} PRD(s) skipped after failure")
    return 0 if all(code == 0 for _, _, code in results) and not skipped else 1
