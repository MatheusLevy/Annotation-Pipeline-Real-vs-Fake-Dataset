import json
import os
import shutil

def read_assigned_split(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        assigned_split: dict = json.load(file)
    return assigned_split

def read_assigned_folder(folder_path: str) -> list[str]:
    file_names: list[str] = os.listdir(folder_path)
    return file_names

def create_assigned_images_folder(assigned_config: dict) -> None:
    assigned_folder: str = "./assigned_batches"
    target_folder = os.path.join(assigned_folder, assigned_config['Assigned'])
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)
    os.makedirs(target_folder, exist_ok=True)

def create_assingned_annotated_folder(assigned_config: dict) -> None:
    assigned_annotated_folder: str = "./annotated"
    target_folder = os.path.join(assigned_annotated_folder, assigned_config['Assigned'])
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)
    os.makedirs(target_folder, exist_ok=True)

def copy_assigned_images(assigned_config: dict) -> None:
    assigned_folder: str = f"./assigned_batches/{assigned_config['Assigned']}"
    for image in assigned_config['images']:
        source_path: str = f"./images/{image}"
        destination_path: str = f"{assigned_folder}/{image}"
        shutil.copy2(source_path, destination_path)

if __name__ == "__main__":
    assigneds_batch_folder: str = "./assigned"
    assigneds_configs = read_assigned_folder(assigneds_batch_folder)
    for assigned_config_file in assigneds_configs:
        assigned_config: dict = read_assigned_split(os.path.join(assigneds_batch_folder, assigned_config_file))
        create_assigned_images_folder(assigned_config)
        create_assingned_annotated_folder(assigned_config)
        copy_assigned_images(assigned_config)