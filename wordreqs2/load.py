import pandas as pd
from . import md_spec


def get_spec(doc_id: str):
    spec = md_spec.parse_file(f"tmp/{doc_id}.md")
    return spec


def get_reqs_as_df(doc_id: str) -> pd.DataFrame:
    spec = get_spec(doc_id)
    data = {
        "doc_id": [],
        "req_id": [],
        "contents": [],
    }

    for req in spec.reqs:
        data["doc_id"].append(doc_id)
        data["req_id"].append(req.id)
        data["contents"].append(req.content)
    
    return pd.DataFrame(data)


def get_trace_as_df(doc_id: str, parent_doc_id: str) -> pd.DataFrame:
    spec = get_spec(doc_id)
    data = {
        "doc_id": [],
        "req_id": [],
        "to_doc_id": [],
        "to_req_id": [],
    }

    for req in spec.reqs:
        for req_trace_id in req.req_trace_ids:
            data["doc_id"].append(doc_id)
            data["req_id"].append(req.id)
            data["to_doc_id"].append(parent_doc_id)
            data["to_req_id"].append(req_trace_id)

    return pd.DataFrame(data)


class ReqDB:
    def __init__(self, config):
        self.reqs: pd.DataFrame = self.build_reqs_table(config)
        self.traces: pd.DataFrame = self.build_traces_table(config)

    def build_reqs_table(self, config) -> pd.DataFrame:
        empty = pd.DataFrame(columns=["doc_id", "req_id", "contents"])
        spec_req_dfs = [get_reqs_as_df(doc_id) for doc_id in config["docs"]]
        req_df = pd.concat([empty] + spec_req_dfs, ignore_index=True)
        return req_df

    def build_traces_table(self, config) -> pd.DataFrame:
        empty = pd.DataFrame(columns=["doc_id", "req_id", "to_doc_id", "to_req_id"])

        spec_trace_dfs = [get_trace_as_df(doc_id, doc_config["parent"])
                        for doc_id, doc_config in config["docs"].items()
                        if "parent" in doc_config]
        trace_df = pd.concat([empty] + spec_trace_dfs, ignore_index=True)
        return trace_df
