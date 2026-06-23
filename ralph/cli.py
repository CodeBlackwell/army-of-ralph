"""CLI entry point — resolves args, then runs a single PRD or a campaign."""

import argparse
from pathlib import Path

from .campaign import find_prd_dirs, run_campaign
from .core import Ralph, detect_mode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ralph",
        description="Ralph — autonomous Claude CLI orchestrator (solo + army)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ralph PRDs/01-feature               # one PRD (mode auto-detected)
  ralph PRDs/01-feature 50            # 50 iterations (solo)
  ralph PRDs/01-feature --army        # force army mode
  ralph PRDs --all                    # run every PRD subdir, in order
        """,
    )
    parser.add_argument("target", nargs="?", default=".",
                        help="PRD dir/file, or a parent dir of PRD subdirs (with --all)")
    parser.add_argument("max_iterations", nargs="?", type=int, default=None,
                        help="Max iterations for solo mode (default: 10)")
    parser.add_argument("sleep", nargs="?", type=int, default=None,
                        help="Sleep seconds between iterations (default: 2)")
    parser.add_argument("-t", "--target", dest="target_named", help="Target dir or file")
    parser.add_argument("-n", "--max-iterations", dest="max_iterations_named", type=int)
    parser.add_argument("-s", "--sleep", dest="sleep_named", type=int)
    parser.add_argument("-a", "--army", action="store_true",
                        help="Force army mode (otherwise auto-detected from agents/ dir)")
    parser.add_argument("--all", action="store_true",
                        help="Run every */PRD.md subdir under target, in name order")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    target = Path(args.target_named or args.target)
    max_iterations = args.max_iterations_named or args.max_iterations or 10
    sleep_seconds = args.sleep_named or args.sleep or 2

    try:
        if args.all:
            return run_campaign(target, max_iterations, sleep_seconds, force_army=args.army)

        resolved = target.resolve()
        target_dir = resolved.parent if resolved.is_file() else resolved
        if resolved.is_dir() and not (resolved / "PRD.md").exists() and find_prd_dirs(resolved):
            print(f"No PRD.md in {resolved}, but it holds PRD subdirs. "
                  f"Run a campaign with: ralph {target} --all")
            return 1

        army = args.army or detect_mode(target_dir)
        return Ralph(target, max_iterations, sleep_seconds, army=army).run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
