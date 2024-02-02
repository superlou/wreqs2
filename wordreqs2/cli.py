import tomllib
from pathlib import Path
import pandas as pd
import argparse
from .load import build_tables, get_spec
from .prepare import run_prepare, copy_docs
from .status import run_status


def trace_down(parent, children):
    parent_reqs = get_spec(parent).reqs
    print(f"🧮 {parent} Requirements:", len(parent_reqs))

    down_map = {parent_req.id: [] for parent_req in parent_reqs}

    all_child_reqs = {} # todo split this up by the source child
    ids_not_found_in_parent = {child: [] for child in children}

    for child in children:
        child_reqs = get_spec(child).reqs
        print(f"🧮 {child} Requirements:", len(child_reqs))
        for child_req in child_reqs:
            all_child_reqs[child_req.id] = child_req
            for parent_req_id in child_req.req_trace_ids:
                try:
                    down_map[parent_req_id].append(child_req.id)
                except KeyError:
                    ids_not_found_in_parent[child].append(parent_req_id)

    if len(ids_not_found_in_parent) > 0:
        total = sum([len(ids) for ids in ids_not_found_in_parent.values()])
        print(f"⚠️ {total} IDs not found in {parent}")
        for child, ids_not_found in ids_not_found_in_parent.items():
            print(child + ": " + ", ".join(ids_not_found))

    untraced_parent_reqs = [parent_id for parent_id, child_id in down_map.items()
                            if len(down_map[parent_id]) == 0]
    
    if len(untraced_parent_reqs) > 0:
        print(f"⚠️ {len(untraced_parent_reqs)} not found in {children}")
        print(", ".join(untraced_parent_reqs))

    # Build report table
    parent_ids = [parent_req.id for parent_req in parent_reqs]
    children_ids = {}
    
    data = {
        "parent": parent_ids
    }
    # print(data)

    df = pd.DataFrame(data=data, columns=["parent"] + children)
    print(df)


def run_traces(config):
    for trace_id, trace_config in config["traces"].items():
        if trace_config["direction"] == "down":
            parent = trace_config["from"]
            children = trace_config["to"]
            trace_down(parent, children)


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["update", "trace", "lint", "status"])
    args = parser.parse_args()

    Path("tmp").mkdir(exist_ok=True)
    config = tomllib.load(open("wreqs.toml", "rb"))

    req_df, trace_df = build_tables(config)

    if args.action == "update":
        copy_docs(config)
        run_prepare(config)
    elif args.action == "trace":
        run_traces(config)
    elif args.action == "status":
        run_status(req_df, config)

    # print(req_df)
    # print(trace_df)
