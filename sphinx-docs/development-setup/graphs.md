# Graphs: Simple RAG vs. Pipeline RAG

This guide provides a deep dive into Maeser’s two primary Retrieval‑Augmented Generation (RAG) pipelines—**Simple RAG** and **Pipeline RAG**—with detailed explanations, professor‑style guidance, and practical code examples. By the end, you’ll know when and how to choose each approach.

---

## Prerequisites

Before you begin, ensure you have:

- A Maeser development environment configured (see `development_setup.md`).
- Python 3.10+ and the Maeser package installed in editable mode.
- At least one FAISS vectorstore (for Simple RAG) and multiple vectorstores (for Pipeline RAG) created via `embedding.md`.

---

## Simple RAG (`get_simple_rag`)

Imagine you’re a university professor specializing in a single course—say, **Medieval Literature**—and students ask you questions only about topics you’ve covered exclusively in that domain. **Simple RAG** is your go‑to approach.

### When to Use Simple Rag

Simple Rag is the best choice when:
- Your application or tutoring session centers around one domain or subject.
- You want minimal complexity and fast responses.

### Conceptual Overview

1. **Single‑Domain Focus**: You have one set of lecture notes, articles, and readings.
2. **Retrieve & Answer**: Upon a student’s question, you quickly flip through your notes, pick the most relevant passages, and craft an answer.
3. **Optional Memory**: If the student follows up, you recall the earlier parts of the conversation (if configured).

### Workflow Details

- **Retrieval**: Queries the designated FAISS index to fetch top‑k document chunks. Think of it as scanning your annotated textbook for the best quotes.
- **Prompt Construction**: Embeds those chunks into a system prompt template, framing the AI as an expert lecturer.
- **Generation**: Invokes the LLM (e.g., GPT-3.5) with the composed prompt, yielding a focused response.

### Code Example

The following code snippet assumes that you have an initialized `ChatSessionManager` object called `sessions_manager` and a `medieval_lit` vectorstore with names `index.faiss` and `index.pkl`. The code also assumes that you have imported config variables from `config_example.py`. Add the following code to your Maeser application (e.g., in `flask_example.py` or your custom script):

```python
from maeser.graphs.simple_rag import get_simple_rag
from langgraph.graph.graph import CompiledGraph

# Create a system prompt for your medieval literature chatbot with appended context. Example prompt:
medieval_prompt: str = """
    You are Professor A. Scholar of Medieval Literature.
    You will answer a student's question about Medieval Literature based on the context provided.
    Don't answer questions about other things.

    {context}
"""

# Build a Simple RAG graph for Medieval Literature
medieval_professor: CompiledGraph = get_simple_rag(
    vectorstore_path=f"{VEC_STORE_PATH}/medieval_lit",
    vectorstore_index="index", # the name of the .faiss and .pkl files in your vectorstore
    memory_filepath=f"{LOG_SOURCE_PATH}/medieval_memory.db",
    system_prompt_text=medieval_prompt,
    model=LLM_MODEL_NAME
)
# Register this graph as the 'medieval' branch
sessions_manager.register_branch(
    branch_name="medieval",
    branch_label="Medieval Literature Q&A",
    graph=medieval_professor,    
)
```

---

## Pipeline RAG (`get_pipeline_rag`)

Now picture a professor teaching a comprehensive curriculum with **homework**, **lab assignments**, and **class discussions**—each requiring domain‑specific expertise. **Pipeline RAG** lets you orchestrate multiple RAG pipelines, routing questions appropriately or combining insights across domains.

### Conceptual Overview

1. **Multi‑Domain Expertise**: Separate vectorstores for Homework, Labs, and Lecture Notes.
2. **Routing & Aggregation**: Determine which domain(s) to tap or merge contexts.
3. **Unified Answer**: Synthesize information into a coherent response, akin to a professor referencing lectures, lab manuals, and homework guidelines.

### Workflow Details

- **Optional Routing**: Classify the student’s question (e.g., “Is this a lab or homework question?”) to decide which vectorstores to query.
- **Retrieval**: Fetch top‑k chunks from each relevant domain’s index.
- **Combine Contexts**: Concatenate or intelligently merge the retrieved chunks.
- **Generation**: Call the LLM with the unified prompt containing all contexts.
- **Memory**: Persist conversation threads across all involved domains for follow‑ups.

### Code Example

> *“Consider this scenario: a student asks about troubleshooting a lab experiment while also relating to a homework theory. Let’s handle both.”*

```python
from maeser.graphs.pipeline_rag import get_pipeline_rag
from maeser.chat.chat_session_manager import ChatSessionManager

# Initialize session manager
sessions = ChatSessionManager()

# Define vectorstore paths for each domain
domains = {
    "homework": "vectorstores/homework",
    "lab":      "vectorstores/lab_manuals",
    "lecture":  "vectorstores/lectures"
}

# Create a Pipeline RAG graph
multi_domain_professor = get_pipeline_rag(
    vectorstore_config=domains,
    memory_filepath="logs/pipeline_memory.db",
    api_key="<OPENAI_API_KEY>",
    system_prompt_text=(
        "You are Professor B, adept at lectures, labs, and homework. "
        "Use these contexts to guide your answer: {context}"
    ),
    model="gpt-4o"
)

# Register the pipeline branch
sessions.register_branch(
    branch_name="curriculum",
    branch_label="Homework & Lab Assistant",
    graph=multi_domain_professor
)
```

> **When to use Pipeline RAG?** When your application spans multiple knowledge bases—like combining theoretical concepts from homework, practical steps from labs, and overarching lectures in one response.

---

## Detailed Comparison

| Feature            | Simple RAG                      | Pipeline RAG                        |
| ------------------ | ------------------------------- | ----------------------------------- |
| Domains            | Single                          | Multiple (Homework, Labs, Lectures) |
| Routing            | N/A                             | Classify & route or query all       |
| Retrieval Steps    | 1                               | 1+ per domain                       |
| Prompt Complexity  | Low                             | Medium to High                      |
| Response Synthesis | One context                     | Aggregated contexts                 |
| Multi‑turn Memory  | Optional single memory file     | Shared memory across domains        |
| Use Case Examples  | Q&A on a specific course module | Comprehensive curricular support    |

---

## Tips & Best Practices

- **Tune chunking: In `simple_rag` and `pipeline_rag`, adjust the number of retrieved chunks for precision vs. breadth.
- **Optimize Prompts**: Tailor the system prompt to clearly define the professor’s persona and expected depth.
- **Memory Management**: Use separate memory files for each branch if you want isolated threads.
- **Combine vs. Route**: If domains rarely overlap, route to a single vectorstore; if they often overlap, merge contexts for richer answers.

---

## Next Steps

- Explore **Custom Graphs** for tool integration (e.g., calculators) in `custom_graphs.md`.
- Review Maeser’s **architecture** in `architecture.md` for internals.
- Contribute your own pipelines and share use cases on GitHub.

