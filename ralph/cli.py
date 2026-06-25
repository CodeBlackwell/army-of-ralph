"""CLI entry point — subcommands: run, watch, init, install-skill, uninstall-skill."""

import argparse
import json
import sys
from importlib.resources import files
from pathlib import Path

from . import ui, watch
from .campaign import find_prd_dirs, run_campaign
from .core import Ralph, detect_mode
from . import __version__

SUBCOMMANDS = {"run", "init", "install-skill", "uninstall-skill", "watch"}
SKILL_PATH = Path.home() / ".claude" / "skills" / "prd" / "SKILL.md"


def _run_direct(args, target: Path, army: bool) -> int:
    ralph = Ralph(target, args.max_iterations or 10, args.sleep or 2,
                  army=army, quiet=args.quiet or args.json, model=args.model,
                  prototype=args.prototype, include_deferred=args.include_deferred)
    if not args.json:
        return ralph.run()

    real_stdout = sys.stdout
    sys.stdout = sys.stderr
    code = ralph.run()
    sys.stdout = real_stdout
    prog = ralph.count_tasks()
    print(json.dumps({
        "mode": "army" if army else "solo", "target": str(ralph.target_dir),
        "exit": code, "completed": prog.completed, "total": prog.total,
    }))
    return code


def _run_collection_direct(args, parent: Path) -> int:
    only = [t for t in args.only.split(",") if t] if args.only else None
    return run_campaign(
        parent, args.max_iterations or 10, args.sleep or 2,
        force_army=args.army, continue_on_fail=args.continue_on_fail,
        only=only, resume=args.resume, quiet=args.quiet, json_output=args.json,
        model=args.model, prototype=args.prototype, include_deferred=args.include_deferred,
    )


def _child_argv(args) -> list[str]:
    """Rebuild this run as a child `ralph run ... --no-watch` invocation."""
    child = [sys.executable, "-m", "ralph", "run", str(args.target)]
    if args.max_iterations is not None:
        child.append(str(args.max_iterations))
    if args.sleep is not None:
        child.append(str(args.sleep))
    if args.army:
        child.append("--army")
    if args.model:
        child += ["--model", args.model]
    if args.prototype:
        child.append("--prototype")
    if args.include_deferred:
        child.append("--include-deferred")
    if args.no_color:
        child.append("--no-color")
    if args.only:
        child += ["--only", args.only]
    if args.resume:
        child.append("--resume")
    if args.continue_on_fail:
        child.append("--continue-on-fail")
    child.append("--no-watch")
    return child


def _cmd_run(args) -> int:
    """Run one PRD or a parent of PRD dirs (auto-detected), under the live dashboard."""
    target = Path(args.target)
    resolved = target.resolve()
    single = resolved.is_file() or (resolved / "PRD.md").exists()
    subdirs = find_prd_dirs(resolved) if (not single and resolved.is_dir()) else []
    if not single and not subdirs:
        print(f"No PRD.md at {resolved} or in its subdirs", file=sys.stderr)
        return 1

    # Default: orchestrate under the live dashboard. Skip it for --no-watch,
    # --json, or non-TTY output (CI), and run inline instead.
    if args.no_watch or args.json or not sys.stdout.isatty():
        if single:
            target_dir = resolved.parent if resolved.is_file() else resolved
            return _run_direct(args, target, args.army or detect_mode(target_dir))
        return _run_collection_direct(args, resolved)
    return watch.supervise(_child_argv(args), resolved)


def _cmd_watch(args) -> int:
    return watch.run(Path(args.target))


def _cmd_init(args) -> int:
    templates = files("ralph") / "templates"
    dest = Path(args.name)
    if dest.exists():
        print(f"{dest} already exists", file=sys.stderr)
        return 1
    dest.mkdir(parents=True)
    (dest / "PRD.md").write_text(
        (templates / "PRD-template.md").read_text(encoding="utf-8"), encoding="utf-8")
    if args.army:
        (dest / "agents").mkdir()
        (dest / "progress").mkdir()
        (dest / "agents" / "example-agent.md").write_text(
            (templates / "example-agent.md").read_text(encoding="utf-8"), encoding="utf-8")
        (dest / "progress" / "example-progress.txt").write_text(
            (templates / "example-progress.txt").read_text(encoding="utf-8"), encoding="utf-8")
    run = f"ralph {dest} --army" if args.army else f"ralph {dest}"
    print(f"Scaffolded {dest}/  →  edit PRD.md, then run: {run}")
    return 0


def _cmd_install_skill(args) -> int:
    src = (files("ralph") / "skills" / "prd-SKILL.md").read_text(encoding="utf-8")
    if SKILL_PATH.exists() and not args.force:
        print(f"{SKILL_PATH} already exists (use --force to overwrite)", file=sys.stderr)
        return 1
    SKILL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SKILL_PATH.write_text(src, encoding="utf-8")
    print(f"Installed PRD skill → {SKILL_PATH}\nUse it in Claude Code with /prd")
    return 0


def _cmd_uninstall_skill(args) -> int:
    if not SKILL_PATH.exists():
        print(f"No PRD skill installed at {SKILL_PATH}", file=sys.stderr)
        return 1
    SKILL_PATH.unlink()
    try:
        SKILL_PATH.parent.rmdir()  # remove the now-empty prd/ dir
    except OSError:
        pass
    print(f"Removed PRD skill → {SKILL_PATH}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ralph", description="Autonomous Claude CLI orchestrator (solo + army)")
    parser.add_argument("--version", action="version", version=f"ralph {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("-a", "--army", action="store_true",
                        help="force army mode (otherwise auto-detected from an agents/ dir)")
    common.add_argument("-m", "--model",
                        help="Claude model for every agent (e.g. sonnet, opus, haiku); "
                             "passed through to `claude --model`")
    common.add_argument("--prototype", action="store_true",
                        help="proof-of-concept mode: agents build the bare minimum and "
                             "the verifier rejects any feature beyond the stories (YAGNI)")
    common.add_argument("-q", "--quiet", action="store_true",
                        help="suppress the Claude output stream and per-iteration banners")
    common.add_argument("--json", action="store_true",
                        help="emit a JSON summary on stdout (human text goes to stderr)")
    common.add_argument("--no-color", action="store_true", help="disable ANSI color")
    common.add_argument("--include-deferred", action="store_true",
                        help="also build deferred phase sections marked 'NOT core scope' "
                             "(default: skip them and stop when core is done)")

    run = sub.add_parser("run", parents=[common],
                         help="run a PRD dir, or a parent of PRD dirs (auto-detected)")
    run.add_argument("target", nargs="?", default=".",
                     help="a PRD dir/file, or a parent dir holding PRD dirs")
    run.add_argument("max_iterations", nargs="?", type=int, default=None,
                     help="max iterations for solo mode (default: 10)")
    run.add_argument("sleep", nargs="?", type=int, default=None,
                     help="sleep seconds between iterations (default: 2)")
    run.add_argument("--no-watch", action="store_true",
                     help="run inline instead of under the live dashboard")
    run.add_argument("--continue-on-fail", action="store_true",
                     help="(multi-PRD) keep going after a PRD fails instead of stopping")
    run.add_argument("--only", help="(multi-PRD) comma-separated name tokens; run only matching dirs")
    run.add_argument("--resume", action="store_true",
                     help="(multi-PRD) skip PRD dirs that are already fully complete")
    run.set_defaults(func=_cmd_run)

    init = sub.add_parser("init", help="scaffold a new PRD directory from templates")
    init.add_argument("name", help="directory to create")
    init.add_argument("-a", "--army", action="store_true",
                      help="also scaffold agents/ + progress/ for army mode")
    init.set_defaults(func=_cmd_init)

    skill = sub.add_parser("install-skill", help="install the PRD skill into ~/.claude/skills")
    skill.add_argument("--force", action="store_true", help="overwrite an existing skill")
    skill.set_defaults(func=_cmd_install_skill)

    unskill = sub.add_parser("uninstall-skill",
                             help="remove the PRD skill from ~/.claude/skills")
    unskill.set_defaults(func=_cmd_uninstall_skill)

    w = sub.add_parser("watch", help="live read-only dashboard for a PRD dir")
    w.add_argument("target", nargs="?", default=".", help="PRD directory to watch")
    w.set_defaults(func=_cmd_watch)
    return parser


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        argv = ["--help"]
    elif argv[0] not in SUBCOMMANDS and argv[0] not in ("-h", "--help", "--version"):
        argv = ["run"] + argv  # bare `ralph <dir>` is shorthand for `ralph run <dir>`

    args = _build_parser().parse_args(argv)
    if getattr(args, "no_color", False) or getattr(args, "json", False):
        ui.set_color(False)

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
