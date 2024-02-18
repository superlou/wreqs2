import tomllib
from wordreqs2.load import ReqDB
from wordreqs2.prepare import run_prepare, copy_docs


def build_req_db(config_file) -> ReqDB:
    config = tomllib.load(open(config_file, "rb"))
    run_prepare(config["docs"])
    return ReqDB(config)


def test_lint_no_shall_or_may():
    db = build_req_db("tests/examples/wreqs.toml")