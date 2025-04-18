# Custom Graphs: Advanced RAG Workflows

This guide explores how to extend Maeser’s default pipelines by building **custom LangGraph graphs**. Beyond the built‑in Simple and Pipeline RAG, you can create multi‑step workflows, integrate external tools, and implement conditional logic to tailor AI tutoring experiences to your needs.

---

## Prerequisites

- A Maeser development environment set up (`development_setup.md`).
- Python 3.10+ with Maeser and LangGraph installed (`pip install -e .` includes LangGraph).
- Familiarity with Simple RAG (`simple_rag`) and Pipeline RAG (`pipeline_rag`) workflows.

---

## 1. Why Build Custom Graphs?

While **Pipeline RAG** can query multiple domains, real‑world tutoring often requires:

- **Multi‑step Reasoning**: Break complex queries into sub‑questions or tool calls (e.g., math calculations).
- **Conditional Branching**: Route a question based on classification or user input before retrieval.
- **Tool Integration**: Connect calculators, external APIs, or verification checks mid‑workflow.
- **Dynamic Prompts**: Adapt system messages based on intermediate results or user feedback.

Custom graphs let you compose these behaviors into a coherent pipeline, giving you full control over your tutoring logic.

---

## 2. Building a Custom Graph with LangGraph

LangGraph’s **GraphBuilder** API allows you to define states (nodes) and transitions (edges) for your workflow.

### 2.1 Import & Initialize

```python
from langgraph.graph import GraphBuilder
from maeser.chat.chat_session_manager import ChatSessionManager

sessions = ChatSessionManager()
builder = GraphBuilder()
```

### 2.2 Define Retrieval State(s)

Add one or more retrieval states using Maeser’s retriever functions:

```python
# Single‑domain retrieval
builder.add_state(
    name="retrieve_notes",
    function=lambda inputs: simple_retrieve(
        vectorstore_path="vectorstores/notes",
        query=inputs["question"], top_k=5
    )
)
```

Or for multiple domains:
```python
builder.add_state(
    name="retrieve_homework",
    function=lambda inputs: simple_retrieve(
        vectorstore_path="vectorstores/homework",
        query=inputs['question'], top_k=3
    )
)
builder.add_state(
    name="retrieve_lecture",
    function=lambda inputs: simple_retrieve(
        vectorstore_path="vectorstores/lectures",
        query=inputs['question'], top_k=3
    )
)
```

### 2.3 Add Tool or Classification States

Integrate tools or classification chains:

```python
# Classification: decide domain
builder.add_state(
    name="classify_domain",
    function=lambda inputs: llm_classify(
        prompt="Classify the question as 'homework' or 'lecture': {question}",
        inputs={"question": inputs['question']}
    )
)

# Calculator tool
builder.add_state(
    name="calculate",
    function=lambda inputs: external_calculator(
        expression=inputs['question']
    )
)
```

### 2.4 Define Generation State

Use an LLM state to generate the final answer:

```python
builder.add_state(
    name="generate_answer",
    function=lambda inputs: llm_generate(
        prompt=(
            "You are an expert tutor. Use contexts: {contexts}\n"
            "Provide a clear, step‑by‑step answer."
        ),
        inputs={"contexts": inputs['contexts']}
    )
)
```

### 2.5 Connect States with Edges

Map the flow of data between states:

```python
# Simple chain: retrieve -> generate
builder.add_edge("retrieve_notes", "generate_answer")

# Multi‑domain: classify -> respective retrieves -> merge -> generate
builder.add_edge("classify_domain", "retrieve_homework", condition=lambda res: res=='homework')
builder.add_edge("classify_domain", "retrieve_lecture", condition=lambda res: res=='lecture')
builder.add_edge("retrieve_homework", "generate_answer")
builder.add_edge("retrieve_lecture", "generate_answer")

# Calculator branch
builder.add_edge("classify_domain", "calculate", condition=lambda res: res=='math')
builder.add_edge("calculate", "generate_answer")
```

### 2.6 Compile & Register

Compile your graph and register it with Maeser:

```python
custom_graph = builder.compile()
sessions.register_branch(
    branch_name="custom_tutor",
    branch_label="Advanced Tutor",
    graph=custom_graph
)
```

---

## 3. Example: Math Tutor with Calculator

This example shows a graph that:
1. Classifies if the question is a math problem.
2. If math, sends it to a calculator tool.
3. Otherwise, retrieves from lecture notes.
4. Generates a final, explanatory answer.

```python
builder = GraphBuilder()
builder.add_state("classify", classify_math_or_topic)
builder.add_state("calc", external_calculator)
builder.add_state("retrieve_notes", notes_retriever)
builder.add_state("answer", llm_generate)
builder.add_edge("classify", "calc", condition=lambda x: x=='math')
builder.add_edge("classify", "retrieve_notes", condition=lambda x: x!='math')
builder.add_edge("calc", "answer")
builder.add_edge("retrieve_notes", "answer")

graph = builder.compile()
sessions.register_branch("math_tutor","Math & Theory Tutor",graph)
```

---

## 4. Best Practices & Tips

- **Design for Clarity**: Keep branches simple; avoid excessive states.
- **Reuse Components**: Leverage `simple_retrieve`, `llm_generate`, and other utility functions.
- **Manage Memory**: Pass `memory_filepath` to `sessions_manager` if you need state across turns.
- **Test Iteratively**: Build and test each branch separately before combining.

---

## 5. Next Steps

- Read **`graphs.md`** for built‑in pipelines.
- Experiment with external tools (e.g., web search) by adding new states.
- Share your custom graphs with the Maeser community via GitHub.
