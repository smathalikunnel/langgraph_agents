from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
class State(TypedDict):
    messages:Annotated[list, add_messages]
graph = StateGraph(State)
graph = graph.compile()
print(graph.invoke({"messages":"hi there"}))