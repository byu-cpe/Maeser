# Custom Graphs: Advanced RAG Workflows

This guide explores how to extend Maeser’s default pipelines by building **custom LangGraph graphs**. Beyond the built‑in Simple and Pipeline RAG, you can create multi‑step workflows, integrate external tools, and implement conditional logic to tailor AI tutoring experiences to your needs.

---

## Prerequisites

- A Maeser development environment set up ([Development Setup](development_setup)).
- Python 3.10+ with Maeser and LangGraph installed (`pip install -e .` includes LangGraph).
- Familiarity with Simple RAG (`simple_rag`) and Pipeline RAG (`pipeline_rag`) workflows. (Return to [Section 4](graphs) if you aren't familiar)

---

## Why Build Custom Graphs?

While **Pipeline RAG** can query multiple domains, real‑world tutoring often requires:

- **Multi‑step Reasoning**: Break complex queries into sub‑questions or tool calls (e.g., math calculations).
- **Conditional Branching**: Route a question based on classification or user input before retrieval.
- **Tool Integration**: Connect calculators, external APIs, or verification checks mid‑workflow.
- **Dynamic Prompts**: Adapt system messages based on intermediate results or user feedback.

Custom graphs let you compose these behaviors into a coherent pipeline, giving you full control over your tutoring logic.

---

## Building a Custom Graph with LangGraph

The easiest way to build a **custom graph** is to use the web tool: [LangGraph Builder](https://build.langchain.com/). We will try to explain a langgraph here:

## Nodes
In LangGraph, a node is like a building block — it’s one step in your program’s flow.

More technically:
* A node is a function or a tool that takes some input, does something (like calling a model, running code, or checking a condition), and then returns an output.
* You connect nodes together to form a graph — kind of like a flowchart — where each node passes its result to the next one.

Let’s say you're building a chatbot that answers questions. You could make a LangGraph with nodes like this:

* Start Node – receives the user’s question.
* LLM Node – uses GPT to come up with an answer.
* Output Node – sends the answer back to the user.

Each of those steps is a node.

This is an example of a node in python:
```python
def ask_question_node(input):
    return {"question": input["user_input"]}

def llm_response_node(input):
    # pretend this calls GPT
    return {"answer": "This is a response to: " + input["question"]}
```

## Edges
An edge is the connection between two nodes.

Think of it like a wire or a path that tells LangGraph:
"After this node finishes, go to that one."

When a node finishes its job and returns some output, the edge decides what node to run next.

There are two main types of edges:
* Static Edges – Always go to the same next node, no matter the result.
* Conditional Edges – Choose the next node based on some value in the output.

Let’s say you’re building a flow like this:
* User types a message → (Start node)
* Classify message as 'question' or 'command' → (Classifier node)
* If it's a question, go to AnswerQuestion node
* If it's a command, go to RunCommand node

Here’s what’s happening:
* Each node does some work.
* Each edge tells the system where to go next.
* The edge from Classifier is a conditional edge — it chooses the next node based on the output.

## Conditional Edges
A conditional edge chooses which node to run next based on the output of the current node.

It’s like saying:

* "If the result is X, go this way.
* If the result is Y, go that way."

They let your graph make decisions.

This is useful when:
* You want to branch the logic based on input.
* You’re handling different types of tasks (e.g. questions vs commands).
* You want to loop or exit based on a condition.

For example, you may want to classify an input. You can do so in something like this:
```python
def classify_node(state):
    text = state["user_input"]
    if "?" in text:
        return {"type": "question"}
    else:
        return {"type": "command"}

```
## Cycles
A cycle in LangGraph is when a node can eventually lead back to itself or to an earlier node in the graph.
In simple terms, A cycle lets your program loop or repeat steps.

You use cycles when:
* You want to retry something.
* You want to keep asking the user for more input.
* You need a multi-step process where results feed back into earlier logic.

Logic for this would look something like this:
```csharp
[get_input] → [check_done]
     ↑             ↓
[process_input] ← "not done"
           ↓
         "done" → [end]
```

---

## Best Practices & Tips

- **Design for Clarity**: Keep branches simple; avoid excessive states.
- **Reuse Components**: Leverage `simple_retrieve`, `llm_generate`, and other utility functions.
- **Manage Memory**: Pass `memory_filepath` to `sessions_manager` if you need state across turns.
- **Test Iteratively**: Build and test each branch separately before combining.

---

## Next Steps

- Read [Graphs: Simple RAG vs. Pipline RAG](graphs) for built‑in pipelines.
- Experiment with external tools (e.g., web search) by adding new states.
- Share your custom graphs with the Maeser community via GitHub.
- For more information on langgraphs, you can find documentation [here](https://langchain-ai.github.io/langgraph/?_gl=1*1a1ptos*_ga*MTA4OTcxNDQ3OS4xNzQ3NzUyMzU1*_ga_47WX3HKKY2*czE3NDc3NTIzNTQkbzEkZzEkdDE3NDc3NTIzNjgkajAkbDAkaDA.#)
