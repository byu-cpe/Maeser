"""
© 2024 Blaine Freestone, Carson Bush, Brent Nelson

This file is part of the Maeser usage example.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
"""
import yaml
import os

def load_config():
    """Load configuration from YAML file."""
    # This will load config from the first valid path. /etc/verity.conf has precedence above directories.
    config_paths = [
        'config_example.yaml',  # Current directory
        './config_example.yaml',  # Parent directory (assuming script is run directly in src
        'example/config_example.yaml'
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            with open(path, 'r') as file:
                print(f'Using configuration at {path} (Priority {config_paths.index(path)})')
                return yaml.safe_load(file)
    
    print("Warning: No configuration file found")
    return {}

config = load_config()
MAX_REQUESTS_REMAINING = int(config.get('rate_limit', {}).get('max_requests_remaining'))
TEST_YAML_OUTPUT_PATH = config.get('application', {}).get('test_yaml_output_path')
VEC_STORE_TYPE = config.get('vectorstore', {}).get('vec_store_type', "faiss")
VEC_STORE_PATH = config.get('vectorstore', {}).get('vec_store_path')
LLM_MODEL_NAME = config.get('llm', {}).get('llm_model_name', "gpt4o")
RATE_LIMIT_INTERVAL = int(config.get('rate_limit', {}).get('rate_limit_interval_seconds'))
USERS_DB_PATH = config.get('user_management', {}).get('accounts_db_path')
OPENAI_API_KEY = config.get('api_keys', {}).get('openai_api_key')
GITHUB_CLIENT_ID = config.get('application', {}).get('github_client_id')
GITHUB_CLIENT_SECRET = config.get('api_keys', {}).get('github_client_secret')
GITHUB_AUTH_CALLBACK_URI = config.get('application', {}).get('github_auth_callback_uri')
LOG_SOURCE_PATH = config.get('logging', {}).get('log_source_path')
CHAT_HISTORY_PATH = config.get('user_management', {}).get('chat_history_path')