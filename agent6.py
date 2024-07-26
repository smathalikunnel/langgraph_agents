from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,END
from langchain_openai import ChatOpenAI

from langchain_core.messages import SystemMessage,ToolMessage

from dotenv import load_dotenv

_ = load_dotenv()

from langchain_community.tools.tavily_search import TavilySearchResults

prompt = """You are a smart research assistant. If you need to, Use the search engine to look up information. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!
"""

tool = [TavilySearchResults(max_results=4)]
tool_dict = {t.name:t for t in tool}

print(tool_dict)
llm = ChatOpenAI(model="gpt-3.5-turbo")#, temperature=0)
llm = llm.bind_tools(tool) # IMPORTANT to reassign, it is not an inplace operation

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State):
    message = state["messages"]
    llm_msg = [SystemMessage(content=prompt)] + message
    #llm_msg = message
    response = llm.invoke(llm_msg)

    return {"messages":[response]}

def call_search_tool(state: State):
    print(state["messages"])
    tool_calls = state["messages"][-1].tool_calls
    result = []
    for tool in tool_calls:
        print(f"calling : {tool}")
        response = tool_dict[tool["name"]].invoke((tool["args"]["query"]))
        # print("RESPONSE")
        # print(response)
        result.append(ToolMessage(tool_call_id=tool['id'], name=tool['name'], content=response))
    return {"messages":result}

def call_search(state:State):
    message = state["messages"][-1]
    return len(message.tool_calls) >0

def call_summarise(state: State):
    message = state["messages"]
    prompt = """Answer the question posed by the Human. Only use the context provided by Tool
    in order to answer the question. Do not use search.
   
"""
    llm_msg = [SystemMessage(content=prompt)] + message
    #llm_msg = message
    print("--------------LLM MSG--------------")
    print(llm_msg)
    response = llm.invoke(llm_msg)
    print("++++++++++++++++++response++++++++++++++++++++")
    return {"messages":[response]}

graph = StateGraph(State)
graph.add_node("model",call_model)
graph.add_node("search", call_search_tool)
graph.add_conditional_edges(
    "model",
      call_search, 
      {True: "search", False: END})
graph.add_edge("model","search")
graph.add_edge("search", "summarise")
graph.add_edge("summarise", END)
graph.add_node("summarise", call_summarise)
graph.set_entry_point("model")
graph = graph.compile()
print(graph.get_graph().draw_ascii())
print(graph.invoke({"messages": "who won the last world cup"}))
