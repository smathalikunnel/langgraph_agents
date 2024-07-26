from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_core.messages import ToolMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv

_ = load_dotenv()

class State(TypedDict):
            messages: Annotated[list, add_messages]

class Agent:
    def __init__(self, tools, checkpointer) -> None:
        llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)
        
        graph = StateGraph(State)
        graph.add_node("model",self.call_model)
        graph.add_node("search", self.call_search)
        #graph.add_edge("search", END)
        graph.add_edge("search", "model")
        graph.set_entry_point("model")
        graph.add_conditional_edges("model", self.is_search_needed, {True: "search", False: END})
        self.graph = graph.compile(checkpointer=checkpointer)
        self.tools = {t.name:t for t in tools}
        self.llm = llm.bind_tools(tools)

    
    def call_search(self, state:State):
        tools = state['messages'][-1].tool_calls

        results = []
        for tool in tools:
            print(f"--------------------CALLING : {tool}")
            result = self.tools[tool["name"]].invoke(tool["args"])
            results.append(ToolMessage(content=str(result), name=tool["name"], tool_call_id=tool["id"]))
            return {"messages": results}
    
    def is_search_needed(self, state: State):
           
           message = state["messages"][-1].tool_calls
           return len(message) > 0


    def call_model(self, state: State):
           messages = state["messages"]
           response = self.llm.invoke(messages)
           return {"messages": [response]}
    


    
search = TavilySearchResults(max_results=4)
memory = SqliteSaver.from_conn_string(":memory:")
tools = [search]
app = Agent(tools, memory)
#print(app.graph.invoke({"messages":"check the weather in mumbai today"}))

# for msg in ["what is the weather in mumbai", "how about london", "which one is warmer"]:
#     messages = [HumanMessage(content=msg)]
#     thread = {"configurable":{"thread_id": "1"}}
#     for event in app.graph.stream({"messages":messages}, thread):
#         print(event)
# print(app.graph.invoke({"messages":messages}))
while True:
      user_input = input("user : ")

      if user_input in ["quit", "q"]:
            print("exiting program")
            break
      messages = [HumanMessage(content=user_input)]
      thread = {"configurable":{"thread_id": "1"}}
      for event in app.graph.stream({"messages":messages}, thread):
        print(event)
