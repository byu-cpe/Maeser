# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module is used to locate `config.yaml` and expose its values for use by the example Maeser dynamic implementations/handlers.
**config_paths** determines where this module will look for `config.yaml`.
"""

import yaml
import os


def load_config():
    """Load configuration from YAML file."""
    config_paths = [
        "dynamic_implementations/config.yaml",
        "config.yaml",
        "./config.yaml",
    ]

    for path in config_paths:
        if os.path.exists(path):
            with open(path, "r") as file:
                print(
                    f"Using configuration at {path} (Priority {config_paths.index(path)})"
                )
                return yaml.safe_load(file)

    print("Warning: No configuration file found")
    return {}


config = load_config()

# API Keys
OPENAI_API_KEY = config.get("api_keys", {}).get("openai_api_key")
GITHUB_CLIENT_SECRET = config.get("api_keys", {}).get("github_client_secret")

# Course ID
COURSE_ID: str = config.get("course_id")

# GitHub Auth
GITHUB_CLIENT_ID: str = config.get("github", {}).get("github_client_id")
GITHUB_AUTH_CALLBACK_URI: str = config.get("github", {}).get("github_callback_uri")
GITHUB_TIMEOUT: int = config.get("github", {}).get("timeout", 10)

# LDAP3 Auth
LDAP3_NAME: str = config.get("ldap3", {}).get("name", "CAEDM")
LDAP_SERVER_URLS: list = config.get("ldap3", {}).get("ldap_server_urls", [])
LDAP_BASE_DN: str = config.get("ldap3", {}).get("ldap_base_dn")
LDAP_ATTRIBUTE_NAME: str = config.get("ldap3", {}).get("attribute_name")
LDAP_SEARCH_FILTER: str = config.get("ldap3", {}).get("search_filter")
LDAP_OBJECT_CLASS: str = config.get("ldap3", {}).get("object_class")
LDAP_ATTRIBUTES: list = config.get("ldap3", {}).get("attributes", [])
LDAP_CA_CERT_PATH: str = config.get("ldap3", {}).get("ca_cert_path")
LDAP_CONNECTION_TIMEOUT: int = config.get("ldap3", {}).get("connection_timeout", 5)

# Rate Limiting
MAX_REQUESTS: int = config.get("rate_limit", {}).get("max_requests", 5)
RATE_LIMIT_INTERVAL: int = config.get("rate_limit", {}).get(
    "rate_limit_interval_seconds", 180
)

# Logging
LOG_SOURCE_PATH: str = config.get("logging", {}).get("log_source_path")

# Vector Store
VEC_STORE_PATH: str = config.get("vectorstore", {}).get("vec_store_path")
VEC_STORE_TYPE: str = config.get("vectorstore", {}).get("vec_store_type", "faiss")

# LLM Configuration
LLM_MODEL_NAME: str = config.get("llm", {}).get("llm_model_name", "gpt-4o-mini")
LLM_PROVIDER: str = config.get("llm", {}).get("llm_provider", "openai")
LLM_TOKEN_LIMIT: int = config.get("llm", {}).get("token_limit", 400)

# Embedding Model
EMBED_MODEL: str = config.get("embed", {}).get("embed_model", "text-embedding-3-large")
EMBED_PROVIDER: str = config.get("embed", {}).get("embed_provider", "openai")

# User Management
USERS_DB_PATH: str = config.get("user_management", {}).get("accounts_db_path")
CHAT_HISTORY_PATH: str = config.get("user_management", {}).get("chat_history_path")

# Discord
DISCORD_BOT_TOKEN = config.get("discord", {}).get("discord_token")

# Teams Bot Credentials (Obtain from Azure Bot Service)
TEAMS_APP_ID: str = os.getenv("TEAMS_APP_ID", "")
TEAMS_APP_PASSWORD: str = os.getenv("TEAMS_APP_PASSWORD", "")
