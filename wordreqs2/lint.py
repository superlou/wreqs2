class Lint:
    def __init__(self, doc_id):
        self.doc_id = doc_id


class MalformedReqID(Lint):
    def __init__(self, doc_id, malformed_id):
        super().__init__(doc_id)
        self.malformed_id = malformed_id
    
    def print(self):
        print(f"<{self.doc_id}> {type(self).__name__}: \"{self.malformed_id}\"")


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
                MalformedReqID(req.doc_id, req.req_id)
            )

    return lints


def run_lint(req_df, trace_df, config):
    lints = []
    lints += check_malformed_req_id(req_df, config)

    for lint in lints:
        lint.print()