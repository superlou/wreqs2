from wordreqs2.config import ProjConfig


def test_load_minimal():
    config = {
        "docs": {
            "doc1": {
                "file": "file1.docx",
                "transforms": ["docx-to-md"],
                "req_id_prefix": "doc1-",
            },
            "doc2": {
                "file": "file2.docx",
                "transforms": ["docx-to-md"],
                "req_id_prefix": "doc2-",
            },
        }
    }

    pc = ProjConfig.from_dict(config)
    assert len(pc.docs) == 2
