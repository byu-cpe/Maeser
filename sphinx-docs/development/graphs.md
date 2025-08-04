# Graphs: Simple RAG vs. Pipeline RAG

This guide provides a deep dive into Maeser’s Retrieval‑Augmented Generation (RAG) graphs—**Simple RAG**, **Pipeline RAG**, and **Universal RAG**—with guidance on when to use each graph. By the end of this guide, you’ll know when and how to choose each approach.

This guide provides a description for each RAG graph but does not provide examples. For working implementations of each RAG graph, see the scripts in `example/apps/` and [**Maeser Example (with Flask & User Management)**](./flask_example.md).

---

## Prerequisites

- A Maeser development environment configured (see [**Development Setup**](./development_setup.md)).
- At least one prebuilt vectorstore (for Simple RAG) or multiple vectorstores (for Pipeline or Universal RAG). Two example vectorstores—`byu` and `maeser`—are provided in `example/resources/vectorstores/`. To create a vectorstore with your own content, see [**Embedding New Content**](./embedding.md).

---

## Simple RAG

The Simple RAG only takes in one vectorstore per **chat branch**, forcing the chatbot to stick to one topic per conversation.

### When to Use Simple Rag

Simple Rag is the best choice when:

- Your application or centers around one domain or subject.
- You want minimal complexity and fast responses.

### Simple RAG Workflow

- **Retrieval**: Scans the vectorstore for passages related to the user's question and retrieves the most relevant document chunks.
- **Prompt Construction**: Concatenates the **conversation history**, **prompt instructions**, and **retrieved context** as input for response generation.
- **Generation**: Invokes the LLM with the composed prompt, yielding a focused response.

### Limitations of Simple RAG

- **Only One Vectorstore:** All content used by the chatbot must be embedded into a single vectorstore. This will require you to compile your dataset of resources into one vectorstore and rebuild this vectorstore any time you make changes to your dataset.

---

## Pipeline RAG

The Pipeline RAG takes in multiple vectorstores per chat branch, allowing the chatbot to dynamically choose the most relevant vectorstore when answering a user's question.

### When to use Pipeline RAG

Pipeline RAG is the best choice when:

- Your application spans multiple knowledge bases—such as data from homework, labs, and textbooks.
- Your chatbot needs to dynamically switch between knowledge bases depending on the question it is asked.

### Pipeline RAG Workflow

- **Domain Routing**: Classify the student’s question (e.g., “Is this a lab or homework question?”) to choose which vectorstore to query.
- **Retrieval**: Scans the chosen vectorstore for passages related to the user's question and retrieves the most relevant document chunks.
- **Prompt Construction**: Concatenates the **conversation history**, **prompt instructions**, and **retrieved context** as input for response generation.
- **Generation**: Invokes the LLM with the composed prompt, yielding a focused response.

### Limitations of Pipeline RAG

- **More LLM Calls:** Invokes the LLM to identify most relevant vectorstore before retrieving context, resulting in a slightly higher cost and response time per message.
- **One Vectorstore Per Message:** If the user asks a question relating to multiple vectorstores, the chatbot is limited to only using one of the vectorstores in its retrieval step. (Ex: If the user asks a question related to both the homework and the textbook, the chatbot can retrieve context from either the homework vectorstore or textbook vectorstore, but not both.)

---

## Universal RAG

Like the Pipeline RAG, the Universal RAG takes in multiple vectorstores per chat branch, but unlike the Pipeline RAG, it can retrieve from multiple vectorstores simultaneously, allowing the chatbot to use as many vectorstores as needed to answer a user's question.

In almost all cases, Universal RAG is a better option compared to Pipeline RAG.

### When to use Universal RAG

Universal RAG is the best choice when:

- Your application spans multiple knowledge bases—such as data from homework, labs, and textbooks.
- Your chatbot needs to dynamically choose which knowledge bases to pull from depending on the question it is asked.


---

## Detailed Comparison

| Feature            | Simple RAG                      | Pipeline RAG                             |
| ------------------ | ------------------------------- | ---------------------------------------- |
| Domains            | Single                          | Multiple (Homework, Labs, Lectures)      |
| Routing            | N/A                             | Classify & route to most relevant domain |
| Retrieval Steps    | 1                               | 1+ per domain                            |
| Response Synthesis | One context                     | One context (chosen by relevance)        |
| Use Case Examples  | Q&A on a specific course module | Comprehensive curricular support         |

---

## Next Steps

- Review the scripts in `example/apps/` and [**Maeser Example (with Flask & User Management)**](./flask_example.md) for implementations of each RAG graph.
- Explore **Custom Graphs** for tool integration (e.g., calculators) in [Custom Graphs: Advanced RAG Workflows](custom_graphs).
