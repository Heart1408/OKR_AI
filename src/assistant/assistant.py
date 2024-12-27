import os
from dotenv import load_dotenv
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, RemoveMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.base.llm_model import get_llm
from src.assistant.tool import retrieve

load_dotenv()

llm = get_llm()
memory = MemorySaver()
CHAT_MESSAGE_NUMBER = int(os.getenv("CHAT_MESSAGE_NUMBER", 10))
_content = """
You are a helpful assistant specializing in the OKR (Objectives and Key Results) system.
Your main role is to:
Answer questions related to OKRs.
Provide guidance on how to effectively use OKRs for goal setting and tracking progress.
Suggest Key Results (KRs) for various Objectives based on best practices.
Provide warm, human-like greetings to users and assist them in a friendly, approachable manner.
If a question is outside the scope of OKRs, politely let the user know:
"I’m not able to provide information on that topic, but feel free to ask about OKRs or other related subjects!"
If the question is unclear or too vague, ask the user for more details to ensure accurate guidance:
"Could you please provide more context or clarify your question?
"""

class State(MessagesState):
    summary: str

tools = ToolNode(tools=[retrieve])

def query_or_respond(state: State):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=_content + system_message)] + state["messages"]
    else:
        messages = [SystemMessage(content=_content)] + state["messages"]
    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}

def summarize_conversation(state: State):
    messages = state["messages"]

    if len(messages) > CHAT_MESSAGE_NUMBER:
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

        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-CHAT_MESSAGE_NUMBER]]

        return {"summary": response.content, "messages": delete_messages}
    else:
        return {"messages": state["messages"]}

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
    docs_content = "\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "Create an answer that is closest to the context below:"
        "If the context doesn't contain any information relevant to the question, answer with what you know as an expert on the OKR system."
        "If the question asks to suggest KR for OKR, even though the context does not contain this information, give suggestions to the user like an expert."
        "Including OKRs: ..., then give the KRs one by one. respectively, each KR on 1 line."
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

def delete_tool_messages(state: State):
    return {"messages": [RemoveMessage(id=msg.id) for msg in state["messages"] if (isinstance(msg, ToolMessage) or msg.content=="")]}

graph_builder = StateGraph(State)
graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)
graph_builder.add_node(summarize_conversation)
graph_builder.add_node(delete_tool_messages)

graph_builder.set_entry_point("query_or_respond")

graph_builder.add_edge("query_or_respond", "summarize_conversation")
graph_builder.add_conditional_edges(
    "summarize_conversation",
    tools_condition,
    {"tools": "tools", END: END},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", "delete_tool_messages")
graph_builder.add_edge("delete_tool_messages", END)

graph = graph_builder.compile(checkpointer=memory)

def assistant(query: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        for step in graph.stream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="values",
            config=config,
        ):
            response = step["messages"]
            conversation = []
            for msg in response:
                if hasattr(msg, 'content') and hasattr(msg, 'id'):
                    msg_type = "HumanMessage" if isinstance(msg, HumanMessage) else "AIMessage"
                    conversation.append({
                        "content": msg.content,
                        "id": msg.id,
                        "type": msg_type
                    })

        return conversation
    except Exception as e:
        return f"An error occurred: {str(e)}"
