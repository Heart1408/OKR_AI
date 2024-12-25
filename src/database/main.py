from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
from src.base.llm_model import get_llm
from src.database.tool import tools, get_last_two_check_in_key_result, get_objective_data

llm = get_llm()
llm_with_tools = (llm.bind_tools(tools))

class InputObject(BaseModel):
    object_id: int = Field(..., title="Objective Id")

class OutputAnalysis(BaseModel):
    answer: str = Field(..., title="Answer from model")

def analysis(object_id):
    query = f"""Generate 3 things [Analynis, Evaluation, Improvement advice] of OKR having object_id {object_id} """

    # system = """
    # # 目的：OKRのチェックインデータを分析しKRの改善やアクションプラン作成のアドバイスをもらう。 
    # # 命令文：以下のチェックインの日付、内容、進捗率などの情報に基づき分析結果を作成してください。 
    # # 条件： 
    # 最新2回分のチェックインデータを分析するので進捗率はそれを加味すること 
    # OKR全体の分析の前にOKR内容、OKR作成者、KRそれぞれのチェックイン者を簡潔に表示すること 
    # OKR全体と、KR毎に現状分析、評価、対応策を記載すること。 
    # OKR全体の進捗率は表示しないこと。 
    # 誰が見てもわかるような言葉で表現すること。 
    # 対応策は具体性があるアクションプランにすること。 
    # アクションプランの作成は最新のチェックインデータに対して行うこと。 
    # 結論と対応策に対するアクションプランを入れること 
    # # 補足：具体的であること 
    # # 出力形式：日本語のテキストと5段階の★評価"""
    system = """
        Objective: Analyze OKR check-in data and provide advice for improving KRs along with specific action plans.
        Instructions: Using the provided check-in data, create an analysis following these conditions:
        - Target Data: Analyze the latest two check-ins, considering their progress rates.
        - Display Requirements:Summarize the OKR content, the OKR creator, and the check-in contributors for each KR concisely.
        - Analysis Details: For the entire OKR and for each KR, provide: Current status analysis, Evaluation, Specific improvement actions
        - Progress Rate: Do not display the overall progress rate of the OKR.
        - Clarity: Use clear, understandable language that anyone can follow.
        - Action Plans: Create actionable and specific improvement plans based on the most recent check-in data.
        - Conclusion: Summarize the analysis results and clearly present the action plans.
        Output Format: 
        - Write the output in natural, readable Japanese text
        - Include a 5-star rating system (★) for evaluation.
        """

    messages = [ SystemMessage(system), HumanMessage(query)]

    ai_msg = AIMessage(content='',additional_kwargs={
        'tool_calls': 
        [
            {
                'id': 'call_VkdJdlEkrWjvuQsvZ93lefdM',
                'function': {
                    'arguments': '{"object_id": '+str(object_id)+'}', 'name': 'get_objective_data'
                },
                'type': 'function'
            },
            {
                'id': 'call_0ED0qva3BDBHJUBaOf3EWhIZ',
                'function': {
                    'arguments': '{"object_id": '+str(object_id)+'}', 'name': 'get_last_two_check_in_key_result'
                },
                'type': 'function'
            }
        ],
        'refusal': None}
    )
    messages.append(ai_msg)
    for tool_call in ai_msg.tool_calls:
        selected_tool = {"get_objective_data": get_objective_data, "get_last_two_check_in_key_result": get_last_two_check_in_key_result}[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)
    
    res = llm_with_tools.invoke(messages)

    return res.content

