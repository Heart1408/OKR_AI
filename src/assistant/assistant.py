import os
from dotenv import load_dotenv
from typing import Literal
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.base.llm_model import get_llm
from src.rag.main import retriever

load_dotenv()

llm = get_llm()
genai_docs = "./data_source/generative_ai"
retriever = retriever(data_dir=genai_docs, data_type="pdf")
memory = MemorySaver()
CHAT_MESSAGE_NUMBER = os.getenv("CHAT_MESSAGE_NUMBER") or 10

class State(MessagesState):
    summary: str

@tool
def retrieve(query: str):
    """Retrieve information related to a query."""
    retriever_results = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in retriever_results)

tools = ToolNode(tools=[retrieve])

def query_or_respond(state: State):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    print(response.tool_calls == [])
    print('test', len(messages))
    if response.tool_calls == []:
        messages = state["messages"]
        if len(messages) > CHAT_MESSAGE_NUMBER:
            return summarize_conversation(state)

    return {"messages": [response]}

def should_continue(state: State):
    """Return the next node to execute."""
    messages = state["messages"]
    if len(messages) > CHAT_MESSAGE_NUMBER:
        return "summarize_conversation"
    return END

def summarize_conversation(state: State):
    summary = state.get("summary", "")
    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary": response.content, "messages": delete_messages}

def generate(state: State):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]
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

graph_builder = StateGraph(State)
graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)
graph_builder.add_node(summarize_conversation)
graph_builder.add_node(should_continue)

graph_builder.set_entry_point("query_or_respond")

graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {"tools": "tools", END: END},
)
graph_builder.add_edge("tools", "generate")
# graph_builder.add_edge("generate", END)

graph_builder.add_conditional_edges(
    "generate",
    should_continue,
)
graph_builder.add_edge("summarize_conversation", END)

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
