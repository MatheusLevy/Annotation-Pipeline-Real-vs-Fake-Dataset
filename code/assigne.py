import os
import json
from utils.yaml import read_yaml
from typing import List
from utils.label_studio import get_tasks_studio_project, not_assigned_tasks, update_tasks, update_tasks_in_label_studio_with_new_fields
import pyarrow as pa
import pandas as pd
import dotenv
dotenv.load_dotenv()

def load_assignment_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    return read_yaml(config_path)

def assign_tasks_to_users(config: dict):
    assigneds: List[dict] = config.get("assigneds", [])
    if not assigneds:
        raise ValueError("No users found in the configuration.")
    
    unassigned_tasks: pa.Table = not_assigned_tasks()
    start_index: int = 0
    new_assigned_tasks_batches: List[pd.DataFrame] = []
    for labeller in assigneds:
        batch_size: int = labeller.get("batch_size", 100)
        assigned_name: str = labeller.get("Assigned")
        reviewer_name: str = labeller.get("Reviewer")
        last_index: int = min(start_index + batch_size, len(unassigned_tasks))
        if start_index >= len(unassigned_tasks):
            break
        batch: pd.DataFrame = unassigned_tasks.slice(start_index, last_index - start_index).to_pandas()
        batch['assigned_to'] = assigned_name
        batch['reviewer'] = reviewer_name
        new_assigned_tasks_batches.append(batch)
        start_index = last_index

    return pd.concat(new_assigned_tasks_batches, ignore_index=True) if new_assigned_tasks_batches else pd.DataFrame()

if __name__ == "__main__":
    os.remove("label_studio_data.parquet") if os.path.exists("label_studio_data.parquet") else None
    config_path: str = "assignment_config.yaml"
    config: dict = load_assignment_config(config_path)
    all_tasks: pa.Table = get_tasks_studio_project(os.getenv("BASE_URL"), os.getenv("PROJECT_ID"))
    update_tasks_in_label_studio_with_new_fields(all_tasks)
    assigned_tasks_df: pd.DataFrame = assign_tasks_to_users(config)
    update_tasks(os.getenv("BASE_URL"), os.getenv("PROJECT_ID"), assigned_tasks_df)