import tomllib
from pathlib import Path
import shutil
import pandas as pd
from .docx_to_md import word_to_md, newline_after_meta
from . import md_spec


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


def run_transforms(doc_id :str, filename: str, transforms: list):
    md_filename = f"tmp/{doc_id}.md"
    shutil.copy(filename, md_filename)

    for transform in transforms:
        print(doc_id, transform)
        if transform == "docx-to-md":
            word_to_md(md_filename, md_filename)
        elif transform == "newline-after-meta":
            newline_after_meta(md_filename, md_filename)


def run_prepare(config):
    for doc_id, doc_config in config["docs"].items():
        transforms = doc_config.get("transforms", [])
        if len(transforms) == 0:
            raise NotImplementedError()
        else:
            run_transforms(doc_id, doc_config["file"], transforms)


def get_spec(doc_id: str):
    spec = md_spec.parse_file(f"tmp/{doc_id}.md")
    return spec



def get_reqs_as_df(doc_id: str) -> pd.DataFrame:
    spec = get_spec(doc_id)
    data = {
        "doc_ids": [],
        "req_ids": [],
        "contents": [],
    }

    for req in spec.reqs:
        data["doc_ids"].append(doc_id)
        data["req_ids"].append(req.id)
        data["contents"].append(req.content)
    
    return pd.DataFrame(data)


def get_trace_as_df(doc_id: str, parent_doc_id: str) -> pd.DataFrame:
    spec = get_spec(doc_id)
    data = {
        "doc_ids": [],
        "req_ids": [],
        "to_doc_id": [],
        "to_req_id": [],
    }

    for req in spec.reqs:
        for req_trace_id in req.req_trace_ids:
            data["doc_ids"].append(doc_id)
            data["req_ids"].append(req.id)
            data["to_doc_id"].append(parent_doc_id)
            data["to_req_id"].append(req_trace_id)

    return pd.DataFrame(data)


def build_tables(config) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Table of requirements
    spec_req_dfs = [get_reqs_as_df(doc_id) for doc_id in config["docs"]]
    req_df = pd.concat(spec_req_dfs, ignore_index=True)

    # Trace table
    spec_trace_dfs = [get_trace_as_df(doc_id, doc_config["parent"])
                      for doc_id, doc_config in config["docs"].items()
                      if "parent" in doc_config]
    trace_df = pd.concat(spec_trace_dfs, ignore_index=True)

    return req_df, trace_df


def run_traces(config):
    for trace_id, trace_config in config["traces"].items():
        if trace_config["direction"] == "down":
            parent = trace_config["from"]
            children = trace_config["to"]
            trace_down(parent, children)


def run_cli():
    Path("tmp").mkdir(exist_ok=True)
    config = tomllib.load(open("wreqs.toml", "rb"))
    # run_prepare(config)
    run_traces(config)
    
    # req_df, trace_df = build_tables(config)
    # print(req_df)
    # print(trace_df)
