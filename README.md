# wreqs2
Wreqs is a WYSIWYG document requirements linting and trace tool.

## Installation
The package is currently not available on PyPI, so it must be cloned from this repo, e.g.:

```
git clone https://github.com/superlou/wreqs2.git
cd wreqs2
pip install .
```

## Testing

On Windows, pytest needs to be set for UTF-8: 

```python -X utf8 -m pytest```

## Setup
Create a folder for your wreqs project. Place your documents in it and a configuration file named `wreqs.toml`.

```
wreqs-project-example/
├─  system_spec.docx
├─  module_a_spec.docx
├─  module_b_spec.docx
└─  wreqs.toml
```

The contents of `wreqs.toml` are:

```
[docs.sys]
file = "system_spec.docx"
transforms = ["docx-to-md"]
req_id_prefix = "sys-"  # Requirements in this doc starts with this.
deleted = "Deleted."    # Requirements with this text were deleted.

[docs.moda]
file = "system_spec.docx"
transforms = ["docx-to-md"]
req_id_prefix = "moda-"
parent = "sys"
deleted = "(deleted)"

[docs.modb]
file = "system_spec.docx"
transforms = ["docx-to-md"]
req_id_prefix = "modb-"
parent = "sys"

[traces.sys-down]
direction = "down"
from = "sys"
to = ["moda", "modb"]
```

*Todo: document `import_from` option.*

## Commands
Run the following commands from inside the project folder:

* update - Run transforms on the word docs to generate markdown files for analysis.
* status - Get requirement counts and the next available requirement ID.
* lint - Run lints.
* trace - Run traces.
