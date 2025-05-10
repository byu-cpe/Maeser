# Architecture Overview

This document provides a detailed walkthrough of Maeser’s core architecture. At the center is the **App_Manager**, which initializes and connects all major modules. Below is a graphical representation of the class hierarchy:

```{mermaid}
flowchart LR
  %% Root Flask orchestrator
  A0["Maeser Flask App"] --> A1["App_Manager"]

  %% ChatSessionManager Module
  subgraph ChatModule["ChatSessionManager Module"]
    direction TB
    B0["ChatSessionManager"]
    B0 --> B1["Simple RAG"]
    B0 --> B2["Pipeline RAG"]
    B0 --> B3["chat_interface"]
    B0 --> B4["new_session_api"]
    B0 --> B5["chat_api"]
    B0 --> B6["conversation_history_api"]
  end
  A1 --> B0

  %% ChatLogsManager Module
  subgraph LogsModule["ChatLogsManager Module"]
    direction TB
    E0["ChatLogsManager"]
    E0 --> E1["feedback_api"]
    E0 --> E2["feedback_form_get"]
    E0 --> E3["feedback_form_post"]
    E0 --> E4["training"]
    E0 --> E5["training_post"]
    E0 --> E6["chat_logs_overview"]
    E0 --> E7["display_chat_log"]
  end
  A1 --> E0

  %% UserManager Module
  subgraph UserModule["UserManager Module"]
    direction TB
    C0["UserManager"]
    C0 --> C1["GithubAuthenticator"]
    C0 --> C2["LDAPAuthenticator"]
    C0 --> C3["login_api.*"]
    C0 --> C4["logout"]
    C0 --> C5["manage_users_view"]
    C0 --> C6["user_management_api"]
  end
  A1 --> C0

  %% Jinja2 helpers
  A1 --> D0["Jinja2 Render Helpers"]

```

## Core Components

### App_Manager
- **File:** `maeser/blueprints.py`  
- **Role:** Bootstraps and configures the Flask app, registers routes via blueprints, applies theming, and initializes background tasks (e.g., quota refresh). Everything flows through this central orchestrator.

### ChatSessionManager Module
- **Class:** `ChatSessionManager` (`maeser/chat/chat_session_manager.py`)  
- **Responsibilities:** Manages conversation sessions, routes messages to the appropriate RAG graph, and tracks session metadata.
- **Subcomponents:**
  - **Simple RAG** (`get_simple_rag`): Single-domain retrieval and generation pipeline.
  - **Pipeline RAG** (`get_pipeline_rag`): Multi-domain or routed retrieval pipeline.
- **Controllers:**
  - `chat_interface.controller` (renders UI)
  - `new_session_api.controller` (creates sessions)
  - `chat_api.controller` (handles messages)
  - `conversation_history_api.controller` (fetches past messages)

### ChatLogsManager Module
- **Class:** `ChatLogsManager` (`maeser/chat/chat_logs.py`)  
- **Responsibilities:** Persists all chat logs, including messages, responses, tokens, and cost metrics.
- **Controllers:**
  - `feedback_api.controller` (submit feedback)
  - `feedback_form_get.controller` / `feedback_form_post.controller` (render and process feedback forms)
  - `training.controller` / `training_post.controller` (render and process training data)
  - `chat_logs_overview.controller` (overview of logs)
  - `display_chat_log.controller` (stream a specific log)

### UserManager Module
- **Class:** `UserManager` (`maeser/user_manager.py`)  
- **Responsibilities:** Handles authentication (OAuth, LDAP), user registration, admin/ban status, and rate limiting.
- **Authenticators:**
  - `GithubAuthenticator`
  - `LDAPAuthenticator`
- **Controllers:**
  - `login_api.*` (login/logout routes)
  - `logout.controller`
  - `manage_users_view.controller` (admin UI)
  - `user_management_api.controller` (user CRUD API)

### Jinja2 Render Helpers
- **File:** `maeser/render.py`  
- **Role:** Provides helper functions for Jinja2 templates to render CSS, HTML snippets, and inject dynamic theming variables.

## Request Flow Summary
1. **HTTP Request** arrives at the Flask app.  
2. **App_Manager** routes the request to the proper controller.  
3. **Controllers** interact with **ChatSessionManager** or **UserManager** depending on the endpoint.  
4. **ChatSessionManager** invokes RAG graphs or logs via **ChatLogsManager** for chat operations.  
5. **UserManager** authenticates and manages user data for secure endpoints.  
6. **Render Helpers** generate final HTML/CSS for web responses.

This architecture ensures clear separation of concerns, scalability of RAG pipelines, and maintainable code structure.

