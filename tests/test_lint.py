import tomllib
from wordreqs2.load import ReqDB
from wordreqs2.prepare import run_prepare, copy_docs
from wordreqs2.lint import check_lints, NoShallOrMay


def build_req_db(config_file) -> tuple[ReqDB, dict]:
    config = tomllib.load(open(config_file, "rb"))
    run_prepare(config["docs"])
    return ReqDB(config), config


def test_lint_no_shall_or_may():
    db, config = build_req_db("tests/examples/wreqs.toml")
    lints = [lint for lint in check_lints(db, config) if isinstance(lint, NoShallOrMay)]
    assert len(lints) == 1
    assert lints[0].req_id == "sys1"
    