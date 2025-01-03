import streamlit as st
import sys
import os
import time
import string
import random
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, RemoveMessage, AIMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.rag.file_loader import Loader
from src.rag.vectorstore import VectorDB
from src.base.llm_model import get_llm

llm = get_llm()
memory = MemorySaver()
CHAT_MESSAGE_NUMBER = int(os.getenv("CHAT_MESSAGE_NUMBER", 10))
_content = """
You are a helpful assistant specializing in the OKR (Objectives and Key Results) system.
Your main role is to:
- Retrieve information related to question, even if the question is unrelated to the OKR system.
- Suggest Key Results (KRs) for various Objectives based on best practices.
- Provide warm, human-like greetings to users and assist them in a friendly, approachable manner.
"""

class State(MessagesState):
    summary: str

@tool
def retriever_tool(query: str):
    """Retrieve information related to query."""
    retriever_results = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in retriever_results)

@st.cache_resource
def retriever(data_dir, data_type):
    doc_loaded = Loader(file_type=data_type).load_dir(data_dir, workers=2)
    retriever = VectorDB(documents = doc_loaded).get_retriever()

    return retriever

tools = ToolNode(tools=[retriever_tool])

def query_or_respond(state: State):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retriever_tool])
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
        "Provide an accurate response based on the context below\n"
        "Exceptions: \n"
        "Case 1. If the context does not provide enough information to answer the question, give the most relevant response based on the available context and your knowledge.\n"
        "Case 2. If the context no relevant information:\n"
            "- If the question clearly falls outside the scope of OKRs, politely inform the user: "
            "I cannot provide information on that topic. I am an assistant supporting the OKR system, and I can provide information and answer any questions related to OKRs.\n"
            "- If the question is unclear or too vague, ask the user for more details to ensure an accurate response: "
            "Could you please provide more context or clarify your question?\n"
        "Case 3. If the question is related to suggesting or creating KRs for OKRs, provide suggestions like an OKR expert. Include the OKR(s) followed by 3-6 relevant KRs, each on a separate line.\n"
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

@st.cache_resource
def build_graph():
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
    return graph

def stream_data(data):
    for chunk in data.split(" "):
        yield chunk + " "
        time.sleep(0.04)

def assistant(query: str, thread_id: str):
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}
    try:
        for step in graph.stream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="values",
            config=config,
        ):

            response = step["messages"][-1].content

        return stream_data(response), response
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "AI", "content": "Welcome. How can I assist you today?"},
        ]

    genai_docs = "./data_source/generative_ai"
    retriever = retriever(data_dir=genai_docs, data_type="pdf")
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    query = st.chat_input("Your message")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("Human"):
            st.markdown(query)

        thread_id = st.query_params['threadId'] if 'threadId' in st.query_params else ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        response_stream, response = assistant(query, thread_id)
        st.session_state.messages.append({"role": "AI", "content": response})
        with st.chat_message("AI"):
            st.write_stream(response_stream)
