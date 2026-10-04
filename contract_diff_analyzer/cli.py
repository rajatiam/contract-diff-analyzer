import argparse, json
from pathlib import Path
from .core import analyze, markdown


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare API contracts with JSON or Markdown reports"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("compare")
    sub.add_argument("before")
    sub.add_argument("after")
    sub.add_argument("--fail-on-breaking", action="store_true")
    sub.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args(argv)
    result = analyze(
        json.loads(Path(args.before).read_text(encoding="utf-8")),
        json.loads(Path(args.after).read_text(encoding="utf-8")),
    )
    print(
        markdown(result) if args.format == "markdown" else json.dumps(result, indent=2)
    )
    if args.fail_on_breaking and (result["breaking"] or not result["fully_analyzed"]):
        raise SystemExit(1)
