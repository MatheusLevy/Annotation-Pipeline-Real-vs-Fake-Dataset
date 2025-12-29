import os
import json
import shutil
import argparse
from tqdm import tqdm

def replace_any_extension(file_path: str, new_extension: str) -> str:
    base = os.path.splitext(file_path)[0]
    return f"{base}.{new_extension.lstrip('.')}"

def rename_annotations(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = json.load(file)

    if (file_path.endswith(".json")):
        return
    img_file_path: str = data.get("task", {}).get("data", "").get("image", "")
    img_filename = replace_any_extension(img_file_path, "json")
    img_filename = os.path.basename(img_filename)
    folder_path = os.path.dirname(file_path)
    full_new_path = os.path.join(folder_path, img_filename)
    if full_new_path == file_path:
        print(f"File {file_path} already has the correct name.")
        return
    shutil.move(file_path, full_new_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename annotation files to match their image filenames.")
    parser.add_argument(
        "--directory",
        "-d",
        default="./annotated/Matheus_Levy",
        help="Directory containing annotation JSON files (default: ./annotated/Matheus_Levy)",
    )
    args = parser.parse_args()
    directory = args.directory

    filenames: list[str] = os.listdir(directory)
    for filename in tqdm(filenames):
        full_path = os.path.join(directory, filename)
        try:
            rename_annotations(full_path)
        except Exception as e:
            print(f"Failed to process {full_path}: {e}")
