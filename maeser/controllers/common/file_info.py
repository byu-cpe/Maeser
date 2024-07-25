
from os import path, stat, walk
import yaml
import subprocess
import platform

def get_creation_time(file_path):
    if platform.system() == 'Darwin':  # macOS
        result = subprocess.run(['stat', '-f', '%B', file_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Error getting creation time: {result.stderr}")
        return int(result.stdout.strip())
    elif platform.system() == 'Linux':
        result = subprocess.run(['stat', '-c', '%W', file_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Error getting creation time: {result.stderr}")
        return int(result.stdout.strip())
    else:
        # Fallback for other operating systems
        return int(path.getctime(file_path))


def get_file_info(file_path: str) -> dict:
    """
    Get detailed information from a file and return it as a dictionary.

    Args:
        file_path (str): The path to the file.

    Returns:
        dict: A dictionary containing detailed information about the file.
    """
    def has_feedback(msgs: list) -> bool:
        for msg in msgs:
            if 'liked' in msg:
                return True
        return False
    
    file_info = {}
    try:
        with open(file_path, 'r') as file:
            chat_log = yaml.safe_load(file)
            file_info['has_feedback'] = has_feedback(chat_log.get('messages', []))
            file_info['first_message'] = chat_log.get('messages', [{}])[0]["content"] if len(chat_log.get('messages', [])) > 0 else None
            file_info['user'] = chat_log.get('user', 'unknown user')
            file_info['real_name'] = chat_log.get('real_name', 'Student')
    except Exception as e:
        print(f"Error: Cannot read file {file_path}: {e}")
    return file_info

def get_file_list(source_path: str) -> list[dict]:
    file_list = []
    for root, dirs, files in walk(source_path):
        for file_name in files:
            file_path = path.join(root, file_name)
            if path.isfile(file_path):
                try:
                    created_time = get_creation_time(file_path)
                except (AttributeError, RuntimeError):
                    created_time = int(path.getctime(file_path))
                
                file_stat = stat(file_path)
                file_info = {
                    'name': file_name,
                    'created': created_time,
                    'modified': int(file_stat.st_mtime),
                    'branch': path.basename(root),
                }
                file_info.update(get_file_info(file_path))
                file_list.append(file_info)
    return file_list
