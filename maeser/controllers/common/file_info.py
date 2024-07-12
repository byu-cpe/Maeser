
from os import path, stat, walk
import yaml
import subprocess

def get_creation_time(file_path):
    result = subprocess.run(['stat', '-c', '%W', file_path], stdout=subprocess.PIPE)
    crtime = int(result.stdout)
    
    if crtime == 0:
        raise AttributeError("Creation time attribute is not available")
    
    return crtime

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
            file_info['first_message'] = chat_log.get('messages', [{}])[0].get('content', None)
            file_info['user'] = chat_log.get('user', 'unknown user')
            file_info['real_name'] = chat_log.get('real_name', 'Student')
            
    except Exception as e:
        print(f"Error: Cannot read file {file_path}: {e}")
    return file_info

def get_file_list(source_path: str) -> list[dict]:
    """
    Get the list of files with metadata in the specified folder and its subfolders.

    Args:
        source_path (str): The path to the folder.

    Returns:
        list: The list of files with their metadata.
    """
    file_list = []
    for root, dirs, files in walk(source_path):
        for file_name in files:
            file_path = path.join(root, file_name)
            if path.isfile(file_path):  # Check if the path is a file
                try:
                    created_time = get_creation_time(file_path)
                except AttributeError:
                    created_time = stat(file_path).st_ctime
                
                file_stat = stat(file_path)
                file_info = {
                    'name': file_name,
                    'created': created_time,
                    'modified': file_stat.st_mtime,
                    'branch': path.basename(root),  # Get the branch name from the directory
                }
                # Update file_info with additional details from get_file_info
                file_info.update(get_file_info(file_path))
                file_list.append(file_info)
    return file_list
