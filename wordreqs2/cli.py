import tomllib
from pathlib import Path
import pandas as pd
import argparse
from .load import build_tables, get_spec
from .prepare import run_prepare, copy_docs
from .status import run_status
from .lint import run_lint
from .trace import run_traces


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["update", "trace", "lint", "status"])
    parser.add_argument("-su", "--skip-update", action="store_true",
                        help="skip update before actions")
    args = parser.parse_args()

    Path("tmp").mkdir(exist_ok=True)
    config = tomllib.load(open("wreqs.toml", "rb"))

    if args.action == "update" or not args.skip_update:
        copy_docs(config)
        run_prepare(config)

        if args.action == "update":
            return

    req_df, trace_df = build_tables(config)

    if args.action == "trace":
        run_traces(config, req_df, trace_df)
    elif args.action == "status":
        run_status(req_df, config)
    elif args.action == "lint":
        run_lint(req_df, trace_df, config)
