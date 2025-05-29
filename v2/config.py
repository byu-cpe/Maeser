"""
© 2024 Gohaun Manley

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
    config_paths = [
        'config.yaml',
        './config.yaml',
        'v2/config.yaml'
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            with open(path, 'r') as file:
                print(f'Using configuration at {path} (Priority {config_paths.index(path)})')
                return yaml.safe_load(file)
    
    print("Warning: No configuration file found")
    return {}

config = load_config()

# API Keys
OPENAI_API_KEY = config.get('api_keys', {}).get('openai_api_key')
GITHUB_CLIENT_SECRET = config.get('api_keys', {}).get('github_client_secret')

# GitHub Auth
GITHUB_CLIENT_ID = config.get('github', {}).get('github_client_id')
GITHUB_AUTH_CALLBACK_URI = config.get('github', {}).get('github_callback_uri')
GITHUB_TIMEOUT = config.get('github', {}).get('timeout', 10)

# LDAP3 Auth
LDAP3_NAME = config.get('ldap3', {}).get('name', 'CAEDM')
LDAP_SERVER_URLS = config.get('ldap3', {}).get('ldap_server_urls', [])
LDAP_BASE_DN = config.get('ldap3', {}).get('ldap_base_dn')
LDAP_ATTRIBUTE_NAME = config.get('ldap3', {}).get('attribute_name')
LDAP_SEARCH_FILTER = config.get('ldap3', {}).get('search_filter')
LDAP_OBJECT_CLASS = config.get('ldap3', {}).get('object_class')
LDAP_ATTRIBUTES = config.get('ldap3', {}).get('attributes', [])
LDAP_CA_CERT_PATH = config.get('ldap3', {}).get('ca_cert_path')
LDAP_CONNECTION_TIMEOUT = config.get('ldap3', {}).get('connection_timeout', 5)

# Rate Limiting
MAX_REQUESTS = config.get('rate_limit', {}).get('max_requests', 5)
RATE_LIMIT_INTERVAL = config.get('rate_limit', {}).get('rate_limit_interval_seconds', 180)

# Logging
LOG_SOURCE_PATH = config.get('logging', {}).get('log_source_path')

# Vectorstore
VEC_STORE_PATH = config.get('vectorstore', {}).get('vec_store_path')
VEC_STORE_TYPE = config.get('vectorstore', {}).get('vec_store_type', 'faiss')

# LLM Configuration
LLM_MODEL_NAME = config.get('llm', {}).get('llm_model_name', 'gpt-4o-mini')
LLM_PROVIDER = config.get('llm', {}).get('llm_provider', 'openai')
LLM_TOKEN_LIMIT = config.get('llm', {}).get('token_limit', 400)

# Embedding Model
EMBED_MODEL = config.get('embed', {}).get('embed_model', 'text-embedding-3-large')
EMBED_PROVIDER = config.get('embed', {}).get('embed_provider', 'openai')

# User Management
USERS_DB_PATH = config.get('user_management', {}).get('accounts_db_path')
CHAT_HISTORY_PATH = config.get('user_management', {}).get('chat_history_path')

# Tokens
DISCORD_BOT_TOKEN = config.get('discord', {}).get('discord_token')

# Teams Bot Credentials (Obtain from Azure Bot Service)
TEAMS_APP_ID = os.getenv("TEAMS_APP_ID", "")
TEAMS_APP_PASSWORD = os.getenv("TEAMS_APP_PASSWORD", "")