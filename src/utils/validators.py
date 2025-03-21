from pathlib import Path

def check_path(path):
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Error: The path '{path}' does not exist.")