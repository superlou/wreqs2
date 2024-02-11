import tomllib
from pathlib import Path
import pandas as pd
import argparse
from .load import get_spec, ReqDB
from .prepare import run_prepare, copy_docs
from .status import run_status
from .lint import run_lint
from .trace import run_traces


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["update", "trace", "lint", "status"])
    parser.add_argument("-su", "--skip-update", action="store_true",
                        help="skip update before actions")
    parser.add_argument("-d", "--documents", nargs="+")
    args = parser.parse_args()

    Path("tmp").mkdir(exist_ok=True)
    config = tomllib.load(open("wreqs.toml", "rb"))

    if args.action == "update" or not args.skip_update:
        if args.documents:
            doc_configs = {doc_id: doc_config
                           for doc_id, doc_config in config["docs"].items()
                           if doc_id in args.documents}
        else:
            doc_configs = config["docs"]

        copy_docs(doc_configs)
        run_prepare(doc_configs)

        if args.action == "update":
            return

    db = ReqDB(config)

    if args.action == "trace":
        run_traces(db, config, docs_filter=args.documents)
    elif args.action == "status":
        run_status(db, config, docs_filter=args.documents)
    elif args.action == "lint":
        run_lint(db, config, docs_filter=args.documents)
