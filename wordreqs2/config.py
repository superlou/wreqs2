from dataclasses import dataclass, field
from typing import Optional, Self


@dataclass
class DocConfig:
    doc_id: str
    file: str
    transforms: list[str]
    req_id_prefix: str
    import_from: Optional[str] = None
    parent: Optional[str] = None
    children: list[str] = field(default_factory=list)
    deleted: Optional[str] = None
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


@dataclass
class TraceConfig:
    trace_id: str
    direction: str
    from_: str
    to: list[str]


@dataclass
class ProjConfig:
    docs: dict[str, DocConfig]
    traces: dict[str, TraceConfig]

    @classmethod
    def from_dict(cls, config: dict) -> Self:
        docs = {doc_id: DocConfig(
            doc_id,
            config["file"],
            config["transforms"],
            config["req_id_prefix"],
            import_from=config.get("import_from", None),
            parent=config.get("parent", None),
            children=config.get("children", []),
            deleted=config.get("deleted", None),
            inputs=config.get("inputs", []),
            outputs=config.get("outputs", []),
        ) for doc_id, config in config.get("docs", {}).items()}

        traces = {trace_id: TraceConfig(
            trace_id,
            config["direction"],
            config["from"],
            config["to"],
        ) for trace_id, config in config.get("traces", {}).items()}

        return cls(
            docs=docs,
            traces=traces,
        )