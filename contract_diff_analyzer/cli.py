import argparse, json
from pathlib import Path
from .core import analyze


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Report breaking changes in a supported OpenAPI subset"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("before")
    compare.add_argument("after")
    compare.add_argument("--fail-on-breaking", action="store_true")
    args = parser.parse_args(argv)
    result = analyze(
        json.loads(Path(args.before).read_text(encoding="utf-8")),
        json.loads(Path(args.after).read_text(encoding="utf-8")),
    )
    print(json.dumps(result, indent=2))
    if args.fail_on_breaking and (result["breaking"] or not result["fully_analyzed"]):
        raise SystemExit(1)
