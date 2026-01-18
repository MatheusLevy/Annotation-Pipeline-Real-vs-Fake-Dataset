import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
import pandas as pd
import os
from label_studio_sdk import LabelStudio
from tqdm import tqdm
import dotenv
dotenv.load_dotenv()

PARQUET_PATH: str = "label_studio_data.parquet"

def convert_to_simplified_format(task) -> pa.Table:
    label = "" if len(task.annotations) == 0 else task.annotations[0]['result'][0]['value']['choices'][0]
    assigned_to = "" if 'assigned_to' not in task.data else task.data['assigned_to']
    reviewer = "" if 'reviewer' not in task.data else task.data['reviewer']
    reviewed: bool = False if 'reviewed' not in task.data else task.data['reviewed']
    comments = "" if 'comments' not in task.meta else task.meta['comments']
    review_approved: bool = False if 'review_approved' not in task.data else task.data['review_approved']
    has_to_update: bool = False if ('assigned_to' in task.data and 'reviewer' in task.data and 'reviewed' in task.data and 'comments' in task.meta and 'review_approved' in task.data) else True
    return pa.table({
        "id": [task.id],
        "image_path": [task.data['image']],
        "label": [label],
        "assigned_to": [assigned_to],
        "reviewer": [reviewer],
        "reviewed": [reviewed],
        "comments": [comments],
        "review_approved": [review_approved],
        "update": [has_to_update]
    })

def append_to_parquet(data: list[pa.Table], parquet_file: str):
    new_data: pa.Table = pa.concat_tables(data)
    if os.path.exists(parquet_file):
        previous_data: pa.Table = pq.read_table(parquet_file)
        combined_table: pa.Table = pa.concat_tables([previous_data, new_data])
        pq.write_table(combined_table, parquet_file)
    else:
        pq.write_table(new_data, parquet_file)

def get_tasks_studio_project(base_url: str, project_id: str) -> pa.Table:
    client = LabelStudio(base_url=base_url, api_key=os.getenv("LABEL_STUDIO_API_KEY")) 
    response = client.tasks.list(project=project_id, page_size=100)
    for task in tqdm(response, desc="Fetching tasks from Label Studio"):
            append_to_parquet([convert_to_simplified_format(task)], PARQUET_PATH)
    return pq.read_table(PARQUET_PATH)

def not_assigned_tasks() -> pa.Table:
    table: pa.Table = pq.read_table(PARQUET_PATH)
    filter_mask = pc.equal(table['assigned_to'], "")
    return table.filter(filter_mask)

def update_tasks(base_url: str, project_id: str, tasks: pd.DataFrame) -> None:
    client = LabelStudio(base_url=base_url, api_key=os.getenv("LABEL_STUDIO_API_KEY")) 
    for i in tqdm(range(len(tasks)), desc="Updating tasks in Label Studio"):
        if tasks['update'][i]:
            client.tasks.update(
                id=str(tasks['id'][i]), 
                project=project_id, 
                data={
                    "assigned_to": str(tasks['assigned_to'][i]),
                    "reviewer": str(tasks['reviewer'][i]),
                    "image": str(tasks['image_path'][i]),
                    "review_approved": bool(tasks['review_approved'][i]),
                    "reviewed": bool(tasks['reviewed'][i])
                    },
                meta={
                    "comments": str(tasks['comments'][i])
                    }
                )


def update_tasks_in_label_studio_with_new_fields(all_tasks: pa.Table, batch:int= 1000) -> pa.Table:
    for batch in all_tasks.to_batches(max_chunksize=batch):
        batch: pd.DataFrame = batch.to_pandas()
        update_tasks(os.getenv("BASE_URL"), os.getenv("PROJECT_ID"), batch)
    
    
        