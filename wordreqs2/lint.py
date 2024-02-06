from rich.console import Console
from rich.table import Table
import pandas as pd


class Lint:
    def __init__(self, doc_id):
        pass


class MalformedReqID(Lint):
    def __init__(self, doc_id, malformed_id, content):
        self.doc_id = doc_id
        self.malformed_id = malformed_id
        self.content = content
    
    @property
    def msg(self):
        return f"{self.doc_id}:{type(self).__name__} \\[{self.malformed_id}] {self.content}"


class DuplicateID(Lint):
    def __init__(self, doc_id, duplicate_id, content):
        self.doc_id = doc_id
        self.duplicate_id = duplicate_id
        self.content = content

    @property
    def msg(self):
        return f"{self.doc_id}:{type(self).__name__} \\[{self.duplicate_id}] {self.content}"


class TracedReqNotFound(Lint):
    def __init__(self, doc_id, req_id, parent_doc_id, parent_req_id):
        self.doc_id = doc_id
        self.req_id = req_id
        self.parent_doc_id = parent_doc_id
        self.parent_req_id = parent_req_id

    @property
    def msg(self):
        return f"{self.doc_id}:{type(self).__name__} \\[{self.req_id}] Requirement \"{self.parent_req_id}\" not found in {self.parent_doc_id}"


def check_malformed_req_id(reqs, config) -> []:
    lints = []

    reqs["prefix"] = reqs.doc_id.apply(lambda doc_id: config["docs"][doc_id]["req_id_prefix"])

    for i, req in reqs.iterrows():
        is_bad = False

        if not req.req_id.startswith(req.prefix):
            is_bad = True

        if not req.req_id.replace(req.prefix, "").isdigit():
            is_bad = True

        if is_bad:
            lints.append(
                MalformedReqID(req.doc_id, req.req_id, req.contents)
            )

    return lints


def check_duplicate_req_id(reqs) -> []:
    duplicated_reqs = reqs.loc[reqs.duplicated("req_id", keep=False)]
    lints = [DuplicateID(row.doc_id, row.req_id, row.contents)
             for i, row in duplicated_reqs.iterrows()]

    return lints


def check_trace_req_not_in_parent(reqs, traces) -> []:
    matched = traces.merge(
        reqs, how="left",
        left_on=["to_doc_id", "to_req_id"],
        right_on=["doc_id", "req_id"],
        suffixes=[None, "_parent"]
    ).drop(["contents", "prefix"], axis=1)

    unfound = matched[matched.req_id_parent.isnull()]

    lints = [TracedReqNotFound(row.doc_id, row.req_id, row.to_doc_id, row.to_req_id)
             for i, row in unfound.iterrows()]

    return lints


def run_lint(req_df, trace_df, config):
    lints = []
    lints += check_malformed_req_id(req_df, config)
    lints += check_duplicate_req_id(req_df)
    lints += check_trace_req_not_in_parent(req_df, trace_df)

    console = Console(soft_wrap=True, highlight=False)

    for lint in lints:
        console.print(lint.msg.split("\n")[0], overflow="ellipsis")
    
    # Make summary
    df = pd.DataFrame(data={"lints": lints})
    df["lint_type"] = df.lints.apply(lambda l: type(l).__name__)
    df["doc_id"] = df.lints.apply(lambda l: l.doc_id)
    df = df.groupby(["lint_type", "doc_id"]).count().lints
    df = df.unstack("doc_id", fill_value=0)
    
    print()

    table = Table()
    table.add_column("Lint")
    for col in df.columns:
        table.add_column(col)
    
    for lint_type, row in df.iterrows():
        table.add_row(str(lint_type), *[str(field) for field in row.values])

    console.print(table)
