#!/usr/bin/env python
import argparse
import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()


def runserver(args: argparse.Namespace) -> None:
    uvicorn.run(
        "app.main:app",
        host=args.host or os.getenv("APP_HOST", "127.0.0.1"),
        port=args.port or int(os.getenv("APP_PORT", 8000)),
        reload=args.reload if args.reload is not None else os.getenv("APP_RELOAD", "true").lower() == "true",
        log_level=os.getenv("APP_LOG_LEVEL", "info"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="my-farm management commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dev_parser = subparsers.add_parser("runserver", help="Run the dev server with auto-reload")
    dev_parser.add_argument("--host", default=None)
    dev_parser.add_argument("--port", type=int, default=None)
    dev_parser.add_argument("--reload", dest="reload", action="store_true", default=None)
    dev_parser.add_argument("--no-reload", dest="reload", action="store_false")
    dev_parser.set_defaults(func=runserver)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
