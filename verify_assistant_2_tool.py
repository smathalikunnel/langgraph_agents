from dotenv import load_dotenv
_ = load_dotenv()

from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults


llm = ChatOpenAI(temperature=0.2, model="gpt-4o")

class State(TypedDict):
    messages: Annotated[list,add_messages]


tool = TavilySearchResults(max_results=2)
tools = [tool]

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
    
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools",ToolNode(tools=tools))
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

graph_builder.add_conditional_edges("chatbot", tools_condition,)
graph_builder.add_edge("tools","chatbot")
graph = graph_builder.compile()


while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}, stream_mode="updates"):
        print("----------------------------EVENT--------------------")
        print(event)
        # messages = event["messages"]
        # for message in messages:
        #     print(message)
        for value in event.values():
            
            print("Assistant:", value["messages"][-1].content)
