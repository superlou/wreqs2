from pandas import DataFrame
from rich.console import Console
from rich.table import Table


def trace_down(parent: str, children: list[str], reqs: DataFrame, traces: DataFrame):
    parent_reqs = reqs[reqs.doc_id == parent]
    reqs_count = len(parent_reqs)
    
    print(f"Tracing requirements from {parent} to {', '.join(children)}")

    joined = parent_reqs.merge(
        traces, how="left",
        left_on=["doc_id", "req_id"],
        right_on=["to_doc_id", "to_req_id"],
        validate="one_to_many",
        suffixes=(None, "_child")
    )

    joined = joined.drop(["to_doc_id", "to_req_id"], axis=1)
    joined.doc_id_child = joined.doc_id_child.fillna("(untraced)")
    counts = joined.groupby("doc_id_child").count().doc_id

    table = Table()
    table.add_column()
    table.add_column("Count", justify="right")

    table.add_row(f"Total {parent} requirements", str(reqs_count))

    for doc, count in counts.items():
        table.add_row(doc, str(count))

    console = Console()
    console.print(table)


def run_traces(config, reqs: DataFrame, traces: DataFrame):
    for trace_id, trace_config in config["traces"].items():
        if trace_config["direction"] == "down":
            parent = trace_config["from"]
            children = trace_config["to"]
            trace_down(parent, children, reqs, traces)