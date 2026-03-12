from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_DB = Path("todo.json")


def load_items(db_path: Path = DEFAULT_DB) -> list[dict]:
    if not db_path.exists():
        return []
    return json.loads(db_path.read_text(encoding="utf-8"))


def save_items(items: list[dict], db_path: Path = DEFAULT_DB) -> None:
    db_path.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")


def cmd_add(args: argparse.Namespace) -> None:
    items = load_items()
    items.append({"title": args.title, "done": False})
    save_items(items)
    print(f"added: {args.title}")


def cmd_list(args: argparse.Namespace) -> None:
    items = load_items()
    for index, item in enumerate(items, start=1):
        marker = "x" if item["done"] else " "
        print(f"{index}. [{marker}] {item['title']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("title")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=cmd_list)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
