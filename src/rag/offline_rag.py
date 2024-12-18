from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class Str_PoutputParser(StrOutputParser):
    def __init__(self) -> None:
        super().__init__()

    def parse(self, text: str) -> str:
        return self.extract_answer(text)

    def extract_answer(self,
                       text_response: str,
                       pattern: str = r"Answer:\s*(.*)"
                       ) -> str:
        return text_response
        # match = re.search(pattern, text_response, re.DOTALL)
        # if match:
        #     answer_text = match.group(1).strip()
        #     return answer_text
        # else:
        #     raise ValueError(f"Answer not found in response: {text_response}")

class Offline_RAG:
    def __init__(self, llm) -> None:
        self.llm = llm
        self.prompt = hub.pull('rlm/rag-prompt')
        self.str_parser = Str_PoutputParser()

    def get_chain(self, retriever):
        # query_transform_prompt = ChatPromptTemplate.from_messages(
        #     [
        #         MessagesPlaceholder(variable_name="messages"),
        #         (
        #             "user",
        #             "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
        #         ),
        #     ]
        # )
        # query_transforming_retriever_chain = RunnableBranch(
        #     (
        #         lambda x: len(x.get("messages", [])) == 1,
        #         # If only one message, then we just pass that message's content to retriever
        #         (lambda x: x["messages"][-1].content) | retriever,
        #     ),
        #     # If messages, then we pass inputs to LLM chain to transform the query, then pass to retriever
        #     query_transform_prompt | self.llm | StrOutputParser() | retriever,
        # ).with_config(run_name="chat_retriever_chain")

        # SYSTEM_TEMPLATE = """
        #     Answer the user's questions based on the below context. 
        #     If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

        #     <context>
        #     {context}
        #     </context>
        #     """

        # question_answering_prompt = ChatPromptTemplate.from_messages(
        #     [
        #         (
        #             "system",
        #             SYSTEM_TEMPLATE,
        #         ),
        #         MessagesPlaceholder(variable_name="messages"),
        #     ]
        # )

        # document_chain = create_stuff_documents_chain(self.llm, question_answering_prompt)

        # conversational_retrieval_chain = RunnablePassthrough.assign(
        #     context=query_transforming_retriever_chain,
        # ).assign(
        #     answer=document_chain,
        # )

        # return conversational_retrieval_chain


        input_data = {
            "context": retriever | self.format_docs,
            "question": RunnablePassthrough()
        }
        rag_chain = (
            input_data
            | self.prompt
            | self.llm
            | self.str_parser
        )
        return rag_chain

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
