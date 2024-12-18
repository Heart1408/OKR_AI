from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.base.llm_model import get_llm
from src.rag.main import retriever

llm = get_llm()
genai_docs = "./data_source/generative_ai"
retriever = retriever(data_dir=genai_docs, data_type="pdf")

@tool
def retrieve(query: str):
    """Retrieve information related to a query."""
    retriever_results = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in retriever_results)

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    print(response.tool_calls)

    return {"messages": [response]}

tools = ToolNode(tools=[retrieve])

def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "Answer the user's questions based on the below context."
        "If the context doesn't contain any relevant information to the question, don't make something up and just say \"I don't know\":"
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    response = llm.invoke(prompt)
    return {"messages": [response]}

graph_builder = StateGraph(MessagesState)
graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)
graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

def assistant(query: str):
    config = {"configurable": {"thread_id": "abc123"}}
    try:
        for step in graph.stream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="values",
            config=config,
        ):
            response = step["messages"][-1].content
        
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}"
