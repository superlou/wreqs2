from typing import Self, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
import pandas as pd

from wordreqs2.config import ProjConfig


class Lint:
    def __init__(self, doc_id):
        pass


@dataclass
class BasicDocReqLint(Lint):
    doc_id: str
    req_id: str
    content: str

    @property
    def msg(self):
        return f"{self.doc_id}:{type(self).__name__} \\[{self.req_id}] {self.content}"


class MalformedReqID(BasicDocReqLint):
    @classmethod
    def check(cls, reqs, config: ProjConfig) -> list[Self]:
        lints = []

        reqs["prefix"] = reqs.doc_id.apply(lambda doc_id: config.docs[doc_id].req_id_prefix)

        for i, req in reqs.iterrows():
            is_bad = False

            if not req.req_id.startswith(req.prefix):
                is_bad = True

            if not req.req_id.replace(req.prefix, "").isdigit():
                is_bad = True

            if is_bad:
                lints.append(
                    cls(req.doc_id, req.req_id, req.contents)
                )

        return lints


class DuplicateID(BasicDocReqLint):
    @classmethod
    def check(cls, reqs) -> list[Self]:
        duplicated_reqs = reqs.loc[reqs.duplicated("req_id", keep=False)]
        lints = [cls(row.doc_id, row.req_id, row.contents)
                for i, row in duplicated_reqs.iterrows()]
        return lints


class NoShallOrMay(BasicDocReqLint):
    @classmethod
    def check(cls, reqs) -> list[Self]:
        lints = [
            cls(req.doc_id, req.req_id, req.contents) 
            for i, req in reqs[~reqs.contents.str.contains("shall|may") & ~reqs.is_deleted].iterrows()
        ]
        return lints


class ModifiedSignalNotUsed(Lint):
    pass


@dataclass
class UnsetSignal(Lint):
    doc_id: str
    req_id: str
    signal: str

    @property
    def msg(self):
        return f"{self.doc_id}:{type(self).__name__} \\[{self.req_id}] Signal \"{self.signal}\" is never set"

    @classmethod
    def check(cls, signals, spec_inputs) -> list[Self]:
        lints = []
        try:
            set_signals = signals[signals.modified]["name"].unique()
        except KeyError:
            set_signals = []

        for i, signal in signals[signals.modified == False].iterrows():
            name = signal["name"]
            if name not in set_signals and name not in spec_inputs[signal.doc_id]:
                lints.append(cls(signal.doc_id, signal.req_id, signal["name"]))

        return lints


@dataclass
class UnusedSignal(Lint):
    doc_id: str
    req_id: str
    signal: str

    @property
    def msg(self):
        return f"{self.doc_id}:{type(self).__name__} \\[{self.req_id}] Signal \"{self.signal}\" is never used"

    @classmethod
    def check(cls, signals, spec_outputs) -> list[Self]:
        lints = []
        try:
            unset_signals = signals[signals.modified == False]["name"].unique()
        except KeyError:
            set_signals = []

        for i, signal in signals[signals.modified].iterrows():
            name = signal["name"]
            if name not in unset_signals and name not in spec_outputs[signal.doc_id]:
                lints.append(cls(signal.doc_id, signal.req_id, signal["name"]))

        return lints


class TracedReqNotFound(Lint):
    def __init__(self, doc_id, req_id, parent_doc_id, parent_req_id):
        self.doc_id = doc_id
        self.req_id = req_id
        self.parent_doc_id = parent_doc_id
        self.parent_req_id = parent_req_id

    @property
    def msg(self):
        return f"{self.doc_id}:{type(self).__name__} \\[{self.req_id}] Requirement \"{self.parent_req_id}\" not found in {self.parent_doc_id}"

    @classmethod
    def check(cls, reqs, traces) -> list[Self]:
        matched = traces.merge(
            reqs, how="left",
            left_on=["to_doc_id", "to_req_id"],
            right_on=["doc_id", "req_id"],
            suffixes=[None, "_parent"]
        ).drop(["contents", "prefix"], axis=1)

        unfound = matched[matched.req_id_parent.isnull()]

        lints = [cls(row.doc_id, row.req_id, row.to_doc_id, row.to_req_id)
                for i, row in unfound.iterrows()]

        return lints


def check_lints(db, config: ProjConfig) -> list[Lint]:
    lints = []
    lints += MalformedReqID.check(db.reqs, config)
    lints += DuplicateID.check(db.reqs)
    lints += NoShallOrMay.check(db.reqs)
    lints += TracedReqNotFound.check(db.reqs, db.traces)

    spec_inputs = {
        doc_id: doc_config.inputs
        for doc_id, doc_config in config.docs.items()
    }
    lints += UnsetSignal.check(db.signals, spec_inputs)

    spec_outputs = {
        doc_id: doc_config.outputs
        for doc_id, doc_config in config.docs.items()
    }
    lints += UnusedSignal.check(db.signals, spec_outputs)

    return lints


def run_lint(db, config: ProjConfig, docs_filter: Optional[list[str]]=None):
    lints = check_lints(db, config)

    console = Console(soft_wrap=True, highlight=False)

    docs_filter = docs_filter or list(config.docs.keys())
    lints = [lint for lint in lints
             if lint.doc_id in docs_filter]

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

    table.add_section()
    table.add_row("All", *[str(field) for field in df.stack().groupby("doc_id").sum().values])

    console.print(table)
