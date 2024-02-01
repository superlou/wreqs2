import shutil
import subprocess
from .docx_to_md import word_to_md, newline_after_meta


def copy_docs(config):
    # Using shutil copy gets permissions denied if the file is open.
    # Using Windows' xcopy is a workaround.
    for doc_id, doc_config in config["docs"].items():
        if "copy_from" in doc_config:
            src = doc_config["copy_from"]
            dst = doc_config["file"]
            suppress_overwrite_prompt = "/Y"
            assume_dst_is_file = "/-I"
            hide_file_names = "/Q"
            subprocess.run(
                [
                    "xcopy", src, dst, 
                    suppress_overwrite_prompt, assume_dst_is_file,
                    hide_file_names
                ],
                stdout=subprocess.DEVNULL
            )
            print(f"🚚 Copied {doc_id} to project")


def run_transforms(doc_id :str, filename: str, transforms: list):
    md_filename = f"tmp/{doc_id}.md"
    shutil.copy(filename, md_filename)

    for transform in transforms:
        print(f"🔧 Transforming {doc_id} by {transform}")
        if transform == "docx-to-md":
            word_to_md(md_filename, md_filename)
        elif transform == "newline-after-meta":
            newline_after_meta(md_filename, md_filename)


def run_prepare(config):
    for doc_id, doc_config in config["docs"].items():
        transforms = doc_config.get("transforms", [])
        if len(transforms) == 0:
            raise NotImplementedError()
        else:
            run_transforms(doc_id, doc_config["file"], transforms)
