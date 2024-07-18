# Using Custom Graphs

## Langchain and Langgraph
Maeser utilizes Langchain and Langgraph to create custom, flexible pipelines for any LLM chat application. With this, you could implement any number of application specific tools or prompts. Before using Langgraph ensure that you understand [the basics of Langchain](https://python.langchain.com/v0.2/docs/tutorials/llm_chain/) and have a solid knowledge of [Langchain Expression Language](https://python.langchain.com/v0.2/docs/how_to/).

## Creating a Custom Graph
> **NOTE**: All example code in this section is based on the `SimpleRAG` implementation found at `src/graphs/simple_rag`.
### Step 1: Langchain and Langgraph Fundamentals
This documentation will only outline how to implement a custom graph in Maeser. Follow the [quickstart tutorial](https://langchain-ai.github.io/langgraph/tutorials/introduction/) for Langgraph to learn the fundamentals of building and using a graph in Langgraph. 
### Step 2: Create Sub-Graph from Base Graph
First, we need to build subgraphs, which will be the building blocks of our main graphs.

For the sub-graph to be used in Maeser, you will need to create a child class of `BaseGraph`. 

1) The `BaseGraph` class contains abstract methods that must be implemented in your subclass.

    - process_prompts(self, prompts: Dict[str, str]) -> Dict[str, str]: This method should process the prompts dictionary passed to the constructor and return a modified dictionary as needed for your graph.
      
      ```python
        def process_prompts(self, prompts: Dict[str, str]) -> Dict[str, str]:
            ### Checks for required keys and processes the prompts ###
            required_keys = ['system', 'document']
            for key in required_keys:
                if key not in prompts:
                    raise ValueError(f"Missing required key: {key}")
                
            return {prompt: get_prompt_text(prompts[prompt]) for prompt in prompts}
      ```
    - process_retrievers(self, store_names: List[str]) -> Dict[str, str]: This method should process the retrievers' names and return a dictionary mapping these names to their respective retriever instances or configurations.
      
      ```python
          def process_retrievers(self, vectorstores: Dict[str, str]):
              ### Checks for required keys and processes the retrievers ###
              required_keys = ['documents']
              for key in required_keys:
                  if key not in vectorstores:
                      raise ValueError(f"Missing required key: {key}")
              
              return {vectorstore: get_retriever(vectorstores[vectorstore]) for vectorstore in vectorstores}
      ```
    - get_graph(self) -> StateGraph: This method should construct and return an instance of the graph that your class is designed to work with. You should not set an exit point (in case you want to build bigger graphs with this)

      ```python
      def get_graph(self) -> StateGraph:
          ### Builds the state graph for the simple rag graph ###
          graph = StateGraph(self.graph_state)
          graph.add_node("retrieve", self.retrieve_node)
          graph.add_node("generate", self.generate_node)
          graph.add_edge("retrieve", "generate")
          graph.set_entry_point("retrieve")
          return graph
      ```
2) For the above `get_graph` method you will write class level methods for each node. This means that you can build any possible Langgraph graph within the class. These are the nodes of the `SimpleRAG` class:
    ```python
    ### Graph specific nodes ###

    def retrieve_node(self, state):
        question = state["messages"][-1]
        documents = self.retrievers["documents"].invoke(question)
        return {"retrieved_context": documents}
    
    def generate_node(self, state):
        messages = state["messages"]
        documents = state['retrieved_context']
        generation = self.chain.invoke({"context": documents, "messages": messages[:-1], "input": messages[-1]})
        return {"messages": [generation]}
    ```

### Step 3: Create Graph from Sub-Graph(s)
Creating the actual graph from one or more sub-graphs is done in the `src/chat/graphs.py` file.

1) Create a function that constructs the graph. This should specify the exit point.

    ```python
      simple_rag = SimpleRAG(
          prompts=config["prompts"],
          vectorstores=config["vectorstores"],
          graph_state=BaseGraphState
      ).get_graph()

      simple_rag.set_finish_point("generate")

      return simple_rag
    ```
    In this case, only one sub-graph is used. But, for more complex graphs, you can create large combinations of subgraphs. For more information see [How to create subgraphs](https://langchain-ai.github.io/langgraph/how-tos/subgraph/) from the Langgraph How-to guides.
2) Map your new function to a string in the `graph_map` dictionary.

    ```python
    graph_map = {
        "simple_rag": get_simple_rag,
        ...
    }
    ```
    This will be important for future configuration.

#### Using a Custom Graph State
You can use a custom graph state by adding it to `src/app/chat/graph_states.py`.

## Configuring a Graph to a Chat Branch
Maeser allows for multiple 'chat branches'. This means that you can have multiple types of chats for different purposes with different implementations. These branches are configured in `chat_config.yaml`. Here's an example of what these configurations look like for SimpleRAG:
```yaml
branches:
  - action: homework
    label: Homework Help
    graph:
      type: simple_rag
      prompts:
        system: homework_system
        document: homework_document
      vectorstores:
        documents: homework
```
According to this configuration:
- The `homework` branch will display as *Homework Help* in the user interface.
- The graph is defined as such:
  - It will use the simple_rag (defined in the graph_map as explained above)
  - It will pass {"system": "homework_system", "document": "homework_document"} as the prompts dictionary and {"documents": "homework"} as the vectorstores dictionary.

> **NOTE**: Each graph implementation will have different structures and requirements for the `prompts` and `vectorestores` parameters. Be sure to check each graph's requirements.

## Prompts and Vectorstores
Prompts and vectorstores should be saved at the directory specified in the `prompt_path` and `vec_store_path` configuration variables.

### Prompts
The name of the prompt in the configurations should be the same as the name of its .txt file.

For example, there should be a `homework_system.txt` in the prompts directory.

### Vectorstores
The name of the vectorstore in the configurations should be the same as the name of the index file for that vectorstore.

For more information on vectorstores, see [emedding instructions](./embedding.md)