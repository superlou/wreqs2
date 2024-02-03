import pandas as pd
from rich.console import Console
from rich.table import Table


def safe_int(x: str):
    try:
        return int(x)
    except ValueError:
        return 0


def find_next_id(reqs, prefix_map) -> pd.Series:
    reqs["prefix"] = reqs.doc_id.apply(lambda doc_id: prefix_map[doc_id])
    reqs["req_num"] = [safe_int(id.replace(prefix, ""))
                       for id, prefix in zip(reqs.req_id, reqs.prefix)]

    reqs_max = reqs.groupby("doc_id").max()
    reqs_max.req_num += 1
    
    next_req_id = reqs_max.prefix + reqs_max.req_num.astype(str)
    next_req_id.name = "next_req_id"
    return next_req_id


def run_status(reqs: pd.DataFrame, config: dict):
    prefix_map = {doc_id: doc_config.get("req_id_prefix", "")
                  for doc_id, doc_config in config["docs"].items()}

    req_counts = reqs.groupby("doc_id").count().req_id
    next_req_id = find_next_id(reqs, prefix_map)
    status = pd.concat([req_counts, next_req_id], axis=1)

    table = Table()
    table.add_column("Doc ID")
    table.add_column("Next ID")
    table.add_column("Count", justify="right")

    for doc_id, row in status.iterrows():
        table.add_row(str(doc_id), str(row.next_req_id), str(row.req_id))

    console = Console()
    console.print(table)