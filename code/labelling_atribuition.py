import os
import yaml
import json

def get_available_images(image_folder: str, annotated_folder: str, assigned_folder: str) -> list[str]:
    def remove_extension(filename: str) -> str:
        return os.path.splitext(filename)[0]
    all_images: set[str] = set(os.listdir(image_folder))
    all_images_no_ext: dict[str, str] = {remove_extension(f): f for f in all_images}
    used_images_no_ext: set[str] = set(remove_extension(f) for f in get_assigned_or_labelled_images(annotated_folder, assigned_folder))
    available_no_ext: set[str] = set(all_images_no_ext.keys()) - used_images_no_ext
    available_images: list[str] = [all_images_no_ext[name] for name in sorted(available_no_ext)]
    return available_images

def get_files_batch(available_images: list[str], batch_size: int, start_index: int) -> list[str]:
    batch: list[str] = available_images[start_index:start_index + batch_size]
    return batch

def read_config(config_path: str) -> dict:
    with open(config_path, 'r') as file:
        config: dict = yaml.safe_load(file)
    return config

def create_config_for_assignment(assigned: str, labels: list[str], output_file: str, images: list[str]) -> None:
    config: dict = {
        'Assigned': assigned,
        'labels': labels,
        'images': images
    }
    os.makedirs("./assigned", exist_ok=True)
    with open(f"./assigned/{output_file}", 'w') as file:
        json.dump(config, file, indent=4)

def get_assigned_or_labelled_images(annotated_folder: str, assigned_folder: str) -> list[str]:
    annotated_images: set[str] = set()
    assigned_images: set[str] = set()

    if os.path.exists(annotated_folder):
        annotators: list[str] = os.listdir(annotated_folder)
        for annotator in annotators:
            annotator_path: str = os.path.join(annotated_folder, annotator)
            if os.path.isdir(annotator_path):
                files: list[str] = os.listdir(annotator_path)
                annotated_images.update(files)

    if os.path.exists(assigned_folder):
        assigned_annotators: list[str] = os.listdir(assigned_folder)
        for annotator in assigned_annotators:
            assigned_file: str = os.path.join(assigned_folder, annotator)
            if os.path.isfile(assigned_file):
                try:
                    with open(assigned_file, 'r') as af:
                        data = json.load(af)
                        assigned_list = data.get("images") if isinstance(data, dict) else None
                        if isinstance(assigned_list, list):
                            assigned_images.update(assigned_list)
                except Exception:
                    continue
            
    combined_images: set[str] = annotated_images.union(assigned_images)
    return list(combined_images)

def validate_batch_requirements(config: dict, available_images: list[str]) -> tuple[bool, str]:
    total_required: int = sum(assignment['batch_size'] for assignment in config['assigneds'])
    available_count: int = len(available_images)
    
    if total_required > available_count:
        return False, f"Insufficient images: required {total_required}, available {available_count}"
    
    return True, ""

if __name__ == "__main__":    
    config: dict = read_config("config.yaml")
    annotated_folder: str = "./annotated"
    assigned_folder: str = "./assigned"    
    image_folder: str = config['assigneds'][0]['image_folder']
    total_images: int = len(os.listdir(image_folder))    
    used_images: list[str] = get_assigned_or_labelled_images(annotated_folder, assigned_folder)    
    available_images: list[str] = get_available_images(image_folder, annotated_folder, assigned_folder)
    print(f"Available images: {len(available_images)}")
    
    is_valid, error_message = validate_batch_requirements(config, available_images)
    if not is_valid:
        print(f"{error_message}")
        exit(1)
        
    assigned_index: int = 0 
    
    for assignment in config['assigneds']:
        batch: list[str] = get_files_batch(available_images, assignment['batch_size'], assigned_index)
        
        if len(batch) < assignment['batch_size']:
            print(f"\n⚠️ Warning: Batch for {assignment['Assigned']} has only {len(batch)} images (requested: {assignment['batch_size']})")
        
        assigned_index += assignment['batch_size']
        
        create_config_for_assignment(
            assigned=assignment['Assigned'],
            output_file=assignment['output_file'],
            labels=assignment['labels'],
            images=batch
        )
            
    total_assigned: int = sum(assignment['batch_size'] for assignment in config['assigneds'])
    remaining_images: int = len(available_images) - total_assigned