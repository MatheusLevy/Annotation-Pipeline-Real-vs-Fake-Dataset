import os
import json
import time

def remove_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[0]

def show_annotation_progress():
    image_folder: str = "./images"
    annotations_folder: str = "./annotated"
    total_images: int = len(os.listdir(image_folder))
    annotated_splits: list[str] = os.listdir(annotations_folder)
    annotation_progress: dict[str, float] = {}
    total_annotated: int = 0
    assigned_folder: str = "./assigned"
    assigned_files_hash: list[str] = []

    for split in annotated_splits:
        split_path: str = os.path.join(annotations_folder, split)
        time.sleep(0.1)

        if os.path.isdir(split_path):
            assigned_count = 0
            assigned_file = os.path.join(assigned_folder, f"{split}.json")
            if os.path.isfile(assigned_file):
                try:
                    with open(assigned_file, 'r') as af:
                        data = json.load(af)
                        assigned_images: list[str] = data.get("images", []) if isinstance(data, dict) else []
                        assigned_files_hash = [remove_file_extension(f) for f in assigned_images]
                        if isinstance(assigned_images, list):
                            assigned_count = len(assigned_images)
                except Exception:
                    assigned_count = 0

            if assigned_count == 0:
                assigned_count = len(os.listdir(split_path))

            annotated_files: list[str] = os.listdir(split_path)
            annotated_images_hash: list[str] = [remove_file_extension(f) for f in annotated_files]
            total_annotated_in_split = len(set(annotated_images_hash).intersection(set(assigned_files_hash))) if assigned_files_hash else len(annotated_files)
            progress: float = (total_annotated_in_split / assigned_count) * 100 if assigned_count > 0 else 0
            annotation_progress[split] = round(progress, 2)
            total_annotated += len(annotated_files)
            print(f"  📁 {split}:")
            print(f"    - In this Batch:  {total_annotated_in_split}/{assigned_count} ({progress:.1f}%)")
            print(f"    - Cumulative:    {total_annotated}/{total_images} ({(total_annotated / total_images) * 100:.1f}%)")
   
    with open("annotation_progress.json", 'w') as file:
        json.dump(annotation_progress, file, indent=4)

    total_progress = (total_annotated / total_images) * 100 if total_images > 0 else 0

    for split, progress in annotation_progress.items():
        status = "🟢" if progress >= 80 else "🟡" if progress >= 50 else "🔴"
        print(f"{status} {split:15} | {progress:6.1f}%")

    print("=" * 50)
    print(f"📊 Overall average progress: {total_progress:.1f}%")

if __name__ == "__main__":
    show_annotation_progress()