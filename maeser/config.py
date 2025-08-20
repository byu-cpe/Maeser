# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module is used to locate `config.yaml` and expose its values for use by other modules in the Maeser package.
**config_paths** determines where this module will look for `config.yaml`. Currently, only the working directory is searched.

Attributes:
    OPENAI_API_KEY (str): The API key for an OpenAI LLM.
    GITHUB_CLIENT_SECRET (str): The secret key for a GitHub OAuth2 application.

    COURSE_ID (str): The course ID the module importing this config should use.

    GITHUB_CLIENT_ID (str): The client ID for a GitHub OAuth2 application.
        This should be the same application referenced in OPENAI_API_KEY
    GITHUB_AUTH_CALLBACK_URI (str): the callback route/URL that the user should be sent when GitHub Authentication is complete.
        This should follow the format "http://www.example.com/login/github_callback".
    GITHUB_TIMEOUT (int): The amount of time before a GitHub Authentication attempt should time out. Defaults to 10.

    LDAP3_NAME (str): The name of the LDAP server.
    LDAP_SERVER_URLS (list[str]): The URLs associated with the LDAP server.
    LDAP_BASE_DN (str): The Base Distinguished Name of the LDAP server.
    LDAP_ATTRIBUTE_NAME (str): The attribute name of the LDAP server.
    LDAP_SEARCH_FILTER (str): The search filter of the LDAP server.
    LDAP_OBJECT_CLASS (str): The object class of the LDAP server.
    LDAP_ATTRIBUTES (list): The attributes of the LDAP server.
    LDAP_CA_CERT_PATH (str): The path to the LDAP server's CA certification.
    LDAP_CONNECTION_TIMEOUT (int): The amount of time before an LDAP Authentication attempt should time out. Defaults to 5.

    MAX_REQUESTS (int): The maximum number of requests a user can send before being rate-limited. Defaults to 5.
    RATE_LIMIT_INTERVAL (int): The interval in which requests are granted to a user. Defaults to 180.
    LOG_SOURCE_PATH (str): The path to the chat logs directory. Defaults to "chat_logs".

    VEC_STORE_PATH (str): The path to the courses/vector stores. Defaults to "bot_data".
    VEC_STORE_TYPE (str): The type of vector store. Defaults to "faiss".

    LLM_MODEL_NAME (str): The name of the LLM. Defaults to "gpt-4o-mini"
    LLM_PROVIDER (str): The provider of the LLM. Defaults to "openai"
    LLM_TOKEN_LIMIT (int): The max number of tokens the LLM should process. Defaults to 400.

    EMBED_MODEL (str): The model used to embed user inputs. Defaults to "text-embedding-3-large"
    EMBED_PROVIDER (str): The provider of the embeddings model. Defaults to "openai"

    USERS_DB_PATH (str): The path to the file used to manage the user database. Defaults to "chat_logs/users.db".
    CHAT_HISTORY_PATH (str): The path to the chat history logs. Defaults to "chat_logs".

    DISCORD_BOT_TOKEN (str): The token for a Discord bot.
    DISCORD_INTRO (str): An intro message that the Discord bot should say when prompted.
"""

import yaml
import os


def load_config() -> dict:
    """Searches the working directory for "config.yaml" and loads it via **yaml.safe_load()**."""
    config_paths = [
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
OPENAI_API_KEY: str = config.get("api_keys", {}).get("openai_api_key", "")
GITHUB_CLIENT_SECRET: str = config.get("api_keys", {}).get("github_client_secret", "")

# Course ID
COURSE_ID: str = config.get("course_id", "")

# GitHub Auth
GITHUB_CLIENT_ID: str = config.get("github", {}).get("github_client_id", "")
GITHUB_AUTH_CALLBACK_URI: str = config.get("github", {}).get("github_callback_uri", "")
GITHUB_TIMEOUT: int = config.get("github", {}).get("timeout", 10)

# LDAP3 Auth
LDAP3_NAME: str = config.get("ldap3", {}).get("name", "")
LDAP_SERVER_URLS: list[str] = config.get("ldap3", {}).get("ldap_server_urls", [])
LDAP_BASE_DN: str = config.get("ldap3", {}).get("ldap_base_dn", "")
LDAP_ATTRIBUTE_NAME: str = config.get("ldap3", {}).get("attribute_name", "")
LDAP_SEARCH_FILTER: str = config.get("ldap3", {}).get("search_filter", "")
LDAP_OBJECT_CLASS: str = config.get("ldap3", {}).get("object_class", "")
LDAP_ATTRIBUTES: list = config.get("ldap3", {}).get("attributes", [])
LDAP_CA_CERT_PATH: str = config.get("ldap3", {}).get("ca_cert_path", "")
LDAP_CONNECTION_TIMEOUT: int = config.get("ldap3", {}).get("connection_timeout", 5)

# Rate Limiting
MAX_REQUESTS: int = config.get("rate_limit", {}).get("max_requests", 5)
RATE_LIMIT_INTERVAL: int = config.get("rate_limit", {}).get(
    "rate_limit_interval_seconds", 180
)

# Logging
LOG_SOURCE_PATH: str = config.get("logging", {}).get("log_source_path", "chat_logs")

# Vector Store
VEC_STORE_PATH: str = config.get("vectorstore", {}).get("vec_store_path", "bot_data")
VEC_STORE_TYPE: str = config.get("vectorstore", {}).get("vec_store_type", "faiss")

# LLM Configuration
LLM_MODEL_NAME: str = config.get("llm", {}).get("llm_model_name", "gpt-4o-mini")
LLM_PROVIDER: str = config.get("llm", {}).get("llm_provider", "openai")
LLM_TOKEN_LIMIT: int = config.get("llm", {}).get("token_limit", 400)

# Embedding Model
EMBED_MODEL: str = config.get("embed", {}).get("embed_model", "text-embedding-3-large")
EMBED_PROVIDER: str = config.get("embed", {}).get("embed_provider", "openai")

# User Management
USERS_DB_PATH: str = config.get("user_management", {}).get(
    "accounts_db_path", "chat_logs/users.db"
)
CHAT_HISTORY_PATH: str = config.get("user_management", {}).get(
    "chat_history_path", "chat_logs"
)

# Discord
DISCORD_BOT_TOKEN: str = config.get("discord", {}).get("discord_token", "")
DISCORD_INTRO: str = config.get("discord", {}).get(
    "intro",
    "## 👋 Hi there! I'm @self\n"
    "I'm your digital assistant for this course!\n"
    "I have access to the course textbook and materials, so I can help you with explanations, examples, and guidance whenever you need it.\n"
    "**Let's get started!** Just send me a DM by clicking my name 👉 @self 👈\n",
)
