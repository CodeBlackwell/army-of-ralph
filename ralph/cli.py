"""CLI entry point — subcommands: run, campaign, init, install-skill."""

import argparse
import json
import sys
from importlib.resources import files
from pathlib import Path

from . import ui
from .campaign import find_prd_dirs, run_campaign
from .core import Ralph, detect_mode
from . import __version__

SUBCOMMANDS = {"run", "campaign", "init", "install-skill", "uninstall-skill"}
SKILL_PATH = Path.home() / ".claude" / "skills" / "prd" / "SKILL.md"


def _cmd_run(args) -> int:
    target = Path(args.target)
    resolved = target.resolve()
    if resolved.is_dir() and not (resolved / "PRD.md").exists() and find_prd_dirs(resolved):
        print(f"No PRD.md in {resolved}, but it holds PRD subdirs. "
              f"Run a campaign: ralph campaign {args.target}", file=sys.stderr)
        return 1

    target_dir = resolved.parent if resolved.is_file() else resolved
    army = args.army or detect_mode(target_dir)
    ralph = Ralph(target, args.max_iterations or 10, args.sleep or 2,
                  army=army, quiet=args.quiet or args.json, model=args.model)

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


def _cmd_campaign(args) -> int:
    only = [t for t in args.only.split(",") if t] if args.only else None
    return run_campaign(
        Path(args.target), args.max_iterations or 10, args.sleep or 2,
        force_army=args.army, continue_on_fail=args.continue_on_fail,
        only=only, resume=args.resume, quiet=args.quiet, json_output=args.json,
        model=args.model,
    )


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
    common.add_argument("-q", "--quiet", action="store_true",
                        help="suppress the Claude output stream and per-iteration banners")
    common.add_argument("--json", action="store_true",
                        help="emit a JSON summary on stdout (human text goes to stderr)")
    common.add_argument("--no-color", action="store_true", help="disable ANSI color")

    for name, func, help_text in (
        ("run", _cmd_run, "run a single PRD (mode auto-detected)"),
        ("campaign", _cmd_campaign, "run every */PRD.md subdir under a dir, in name order"),
    ):
        sp = sub.add_parser(name, parents=[common], help=help_text)
        sp.add_argument("target", nargs="?", default=".",
                        help="PRD dir/file, or a parent dir of PRD subdirs")
        sp.add_argument("max_iterations", nargs="?", type=int, default=None,
                        help="max iterations for solo mode (default: 10)")
        sp.add_argument("sleep", nargs="?", type=int, default=None,
                        help="sleep seconds between iterations (default: 2)")
        sp.set_defaults(func=func)
    camp = sub.choices["campaign"]
    camp.add_argument("--continue-on-fail", action="store_true",
                      help="keep going after a PRD fails instead of stopping")
    camp.add_argument("--only", help="comma-separated name tokens; run only matching PRD dirs")
    camp.add_argument("--resume", action="store_true",
                      help="skip PRD dirs that are already fully complete")

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
