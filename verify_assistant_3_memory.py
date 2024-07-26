from dotenv import load_dotenv
_ = load_dotenv()

from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.prebuilt import ToolNode,tools_condition

from langgraph.graph import StateGraph

class State(TypedDict):
    messages: Annotated[list,add_messages]

graph_builder = StateGraph(State)

tool = TavilySearchResults(max_results=2)
tools = [tool]

llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")
llm_w_tools = llm.bind_tools(tools)

def call_model(state:State) ->dict:
    return {"messages": llm_w_tools.invoke(state['messages'])}

graph_builder.add_node("chatbot", call_model)
graph_builder.add_node("tools", ToolNode(tools))

graph_builder.add_conditional_edges("chatbot",tools_condition)
graph_builder.add_edge("tools","chatbot")
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
memory = SqliteSaver.from_conn_string(":memory:")
graph = graph_builder.compile(checkpointer=memory)

print(graph.get_graph().draw_ascii())


config = {"configurable":{"thread_id":1}}
while True: 
    user_ip = input("user:")

    if user_ip in ['quit','q']:
        print("exiting")
        break
    events =  graph.stream({"messages":("human",user_ip)},config, stream_mode="values")
    for event in events:
        event['messages'][-1].pretty_print() 
