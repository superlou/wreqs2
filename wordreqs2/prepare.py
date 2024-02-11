import shutil
import os
import subprocess
from multiprocessing import Pool
from .docx_to_md import word_to_md, newline_after_meta


def copy_docs(doc_configs):
    # Using shutil copy gets permissions denied if the file is open.
    # Using Windows' xcopy is a workaround.
    # Also, xcopy doesn't always seem to have the /-I flag, so a file
    # is made manually first, so it doesn't prompt if the dst is a
    # file or folder.
    for doc_id, doc_config in doc_configs.items():
        if "import_from" in doc_config:
            src = doc_config["import_from"]
            dst = doc_config["file"]

            if not os.path.exists(dst):
                with open(dst, "w"):
                    pass

            suppress_overwrite_prompt = "/Y"
            hide_file_names = "/Q"
            subprocess.run(
                [
                    "xcopy", src, dst, hide_file_names, suppress_overwrite_prompt,
                ],
                stdout=subprocess.DEVNULL, shell=True
            )
            print(f"🚚 Imported {doc_id} to project")


def run_transforms(doc_id :str, filename: str, transforms: list):
    md_filename = f"tmp/{doc_id}.md"
    shutil.copy(filename, md_filename)

    for transform in transforms:
        if transform == "docx-to-md":
            word_to_md(md_filename, md_filename)
        elif transform == "newline-after-meta":
            newline_after_meta(md_filename, md_filename)

        print(f"🔧 Transformed {doc_id} by {transform}")

def run_prepare(doc_configs):
    with Pool(4) as p:
        args = [(doc_id, doc_config["file"], doc_config.get("transforms", []))
                for doc_id, doc_config in doc_configs.items()]
        p.starmap(run_transforms, args)