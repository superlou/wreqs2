import pandas as pd
from . import md_spec
from .md_spec import Spec


def get_spec(doc_id: str):
    spec = md_spec.parse_file(f"tmp/{doc_id}.md")
    return spec


def get_reqs_as_df(doc_id: str, spec: Spec) -> pd.DataFrame:
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


def get_signals_as_df(doc_id: str, spec: Spec) -> pd.DataFrame:
    data = {
        "name": [],
        "modified": [],
        "doc_id": [],
        "req_id": [],
    }

    for req in spec.reqs:
        for signal in req.signals:
            data["doc_id"].append(doc_id)
            data["req_id"].append(req.id)
            data["name"].append(signal)
            data["modified"].append(False)
        
        for signal in req.mod_signals:
            data["doc_id"].append(doc_id)
            data["req_id"].append(req.id)
            data["name"].append(signal)
            data["modified"].append(True)
    
    return pd.DataFrame(data)


def get_trace_as_df(doc_id: str, parent_doc_id: str, spec: Spec) -> pd.DataFrame:
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


def add_is_deleted(reqs: pd.DataFrame, config: dict):
    reqs["is_deleted"] = False
    deleted_text_map = {doc_id: doc_config["deleted"]
                        for doc_id, doc_config in config["docs"].items()
                        if "deleted" in doc_config}

    for doc_id, deleted_text in deleted_text_map.items():
        reqs.loc[reqs.doc_id == doc_id, "is_deleted"] = (reqs.contents == deleted_text)


class ReqDB:
    def __init__(self, config):
        self.specs = {doc_id: get_spec(doc_id) for doc_id in config["docs"]}
        self.reqs = self.build_reqs_table(config)
        self.traces = self.build_traces_table(config)
        self.signals = self.build_signals_table(config)

    def build_reqs_table(self, config) -> pd.DataFrame:
        empty = pd.DataFrame(columns=["doc_id", "req_id", "contents"])
        spec_req_dfs = [get_reqs_as_df(doc_id, spec)
                        for doc_id, spec in self.specs.items()]
        req_df = pd.concat([empty] + spec_req_dfs, ignore_index=True)
        add_is_deleted(req_df, config)
        return req_df

    def build_traces_table(self, config) -> pd.DataFrame:
        empty = pd.DataFrame(columns=["doc_id", "req_id", "to_doc_id", "to_req_id"])

        spec_trace_dfs = [get_trace_as_df(doc_id, doc_config["parent"], self.specs[doc_id])
                          for doc_id, doc_config in config["docs"].items()
                          if "parent" in doc_config]
        trace_df = pd.concat([empty] + spec_trace_dfs, ignore_index=True)
        return trace_df

    def build_signals_table(self, config) -> pd.DataFrame:
        empty = pd.DataFrame(columns=["name", "modified", "doc_id", "req_id"])
        signals_dfs = [get_signals_as_df(doc_id, spec)
                       for doc_id, spec in self.specs.items()]

        signals_df = pd.concat([empty] + signals_dfs, ignore_index=True)
        return signals_df