import tomllib
from pathlib import Path
import pandas as pd
import argparse
from .load import build_tables, get_spec
from .prepare import run_prepare, copy_docs
from .status import run_status
from .lint import run_lint
from .trace import trace_down


def run_traces(config, reqs: pd.DataFrame, traces: pd.DataFrame):
    for trace_id, trace_config in config["traces"].items():
        if trace_config["direction"] == "down":
            parent = trace_config["from"]
            children = trace_config["to"]
            trace_down(parent, children, reqs, traces)


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["update", "trace", "lint", "status"])
    args = parser.parse_args()

    Path("tmp").mkdir(exist_ok=True)
    config = tomllib.load(open("wreqs.toml", "rb"))

    if args.action == "update":
        copy_docs(config)
        run_prepare(config)
    elif args.action == "trace":
        req_df, trace_df = build_tables(config)
        run_traces(config, req_df, trace_df)
    elif args.action == "status":
        req_df, trace_df = build_tables(config)
        run_status(req_df, config)
    elif args.action == "lint":
        req_df, trace_df = build_tables(config)
        run_lint(req_df, trace_df, config)

    # print(req_df)
    # print(trace_df)
