from textwrap import wrap
from rich.console import Console
from rich.text import Text


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


def check_malformed_req_id(reqs, config):
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


def check_duplicate_req_id(reqs):
    lints = []

    duplicated_reqs = reqs.loc[reqs.duplicated("req_id", keep=False)]
    lints = [DuplicateID(row.doc_id, row.req_id, row.contents)
             for i, row in duplicated_reqs.iterrows()]

    return lints


def run_lint(req_df, trace_df, config):
    lints = []
    lints += check_malformed_req_id(req_df, config)
    lints += check_duplicate_req_id(req_df)

    console = Console(soft_wrap=True, highlight=False)

    for lint in lints:
        console.print(lint.msg.split("\n")[0], overflow="ellipsis")