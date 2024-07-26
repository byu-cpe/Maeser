# Creating and Using Custom Graphs

## Creating Custom Graphs

Maeser uses LangGraph compiled state graph objects. 
Refer to the [LangGraph documentation](https://langchain-ai.github.io/langgraph/) for reference and tutorials on how to create custom graphs.

## Using Custom Graphs in Maeser

As shown in the [example application documentation](./flask_example.md) you register compiled state graph objects as branches to the chat sessions manager with its name and label:

```python
compiled_graph = graph_builder.compile()

sessions_manager.register_branch("rag", "Simple RAG", simple_rag)
```