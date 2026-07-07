from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from llm import get_llm
from tools import search_news, read_materials, generate_report


def create_search_agent():
    llm = get_llm(temperature=0.5)
    tools = [search_news]
    system_prompt = """你是一个情报搜集智能体，负责根据用户设定的关键词搜索行业新闻，汇总成原始素材。
    使用 search_news 工具搜索新闻，搜索后素材会自动保存。
    注意：调用 search_news 时必须传入 chat_id 参数，值为当前对话ID。"""
    return create_agent(llm, tools, system_prompt=system_prompt)


def create_analysis_agent():
    llm = get_llm(temperature=0.4)
    tools = [read_materials]
    system_prompt = """你是一个数据分析智能体，负责阅读原始素材，提炼核心观点，判断对业务的影响。
    使用 read_materials 工具读取已搜集的素材，然后进行分析总结。
    注意：调用 read_materials 时必须传入 chat_id 参数，值为当前对话ID。"""
    return create_agent(llm, tools, system_prompt=system_prompt)


def create_report_agent():
    llm = get_llm(temperature=0.5)
    tools = [read_materials, generate_report]
    system_prompt = """你是一个报告撰写智能体，负责把分析结果按照公司固定的周报模板排版生成报告。
    先使用 read_materials 读取素材，然后使用 generate_report 生成报告。
    注意：调用所有工具时必须传入 chat_id 参数，值为当前对话ID。"""
    return create_agent(llm, tools, system_prompt=system_prompt)


search_agent = create_search_agent()
analysis_agent = create_analysis_agent()
report_agent = create_report_agent()


def create_main_agent():
    llm = get_llm(temperature=0.3)
    
    @tool
    def call_search_agent(question: str) -> str:
        """调用情报搜集智能体，搜索行业新闻"""
        result = search_agent.invoke({"messages": [HumanMessage(content=question)]})
        return result["messages"][-1].content
    
    @tool
    def call_analysis_agent(question: str) -> str:
        """调用数据分析智能体，分析素材"""
        result = analysis_agent.invoke({"messages": [HumanMessage(content=question)]})
        return result["messages"][-1].content
    
    @tool
    def call_report_agent(question: str) -> str:
        """调用报告撰写智能体，生成报告"""
        result = report_agent.invoke({"messages": [HumanMessage(content=question)]})
        return result["messages"][-1].content
    
    tools = [call_search_agent, call_analysis_agent, call_report_agent]
    system_prompt = """你是一个智能路由助手，根据用户的问题选择合适的助手来回答：
    - 如果是搜索新闻、搜集情报，使用 call_search_agent
    - 如果是分析素材、提炼观点，使用 call_analysis_agent
    - 如果是生成周报、撰写报告，使用 call_report_agent
    
    工作流程建议：先搜索新闻 → 再分析素材 → 最后生成报告。
    
    当前对话ID: {chat_id}"""
    return create_agent(llm, tools, system_prompt=system_prompt)


main_agent = create_main_agent()


def chat_with_main(user_input: str, history: str = "", chat_id: int = 1) -> str:
    import tools
    tools.current_chat_id = chat_id
    
    system_prompt = f"""你是一个智能路由助手，根据用户的问题选择合适的助手来回答：
    - 如果是搜索新闻、搜集情报，使用 call_search_agent
    - 如果是分析素材、提炼观点，使用 call_analysis_agent
    - 如果是生成周报、撰写报告，使用 call_report_agent
    
    工作流程建议：先搜索新闻 → 再分析素材 → 最后生成报告。
    
    当前对话ID: {chat_id}"""
    
    if history:
        messages = [{"role": "user", "content": f"{system_prompt}\n\n历史对话:\n{history}\n\n当前问题: {user_input}"}]
    else:
        messages = [{"role": "user", "content": f"{system_prompt}\n\n问题: {user_input}"}]
    
    result = main_agent.invoke({"messages": messages})
    return result["messages"][-1].content


def chat_with_specific(agent_name: str, user_input: str, history: str = "", chat_id: int = 1) -> str:
    import tools
    tools.current_chat_id = chat_id
    
    agent_prompts = {
        "search": """你是一个情报搜集智能体，负责根据用户设定的关键词搜索行业新闻，汇总成原始素材。
    使用 search_news 工具搜索新闻，搜索后素材会自动保存。""",
        "analysis": """你是一个数据分析智能体，负责阅读原始素材，提炼核心观点，判断对业务的影响。
    使用 read_materials 工具读取已搜集的素材，然后进行分析总结。""",
        "report": """你是一个报告撰写智能体，负责把分析结果按照公司固定的周报模板排版生成报告。
    先使用 read_materials 读取素材，然后使用 generate_report 生成报告。""",
    }
    
    if history:
        content = f"{agent_prompts.get(agent_name, agent_prompts['search'])}\n\n历史对话:\n{history}\n\n当前问题: {user_input}"
    else:
        content = f"{agent_prompts.get(agent_name, agent_prompts['search'])}\n\n问题: {user_input}"
    
    messages = [{"role": "user", "content": content}]
    
    agents = {
        "search": search_agent,
        "analysis": analysis_agent,
        "report": report_agent,
    }
    agent = agents.get(agent_name, search_agent)
    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content