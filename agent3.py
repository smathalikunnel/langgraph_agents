from dotenv import load_dotenv

_ = load_dotenv()
# create llm
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
# create state
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph

class State(TypedDict):
    messages: Annotated[list, add_messages]

g = StateGraph(State)
# add node
def call_model(state: State):
    message = state["messages"]
    response = model.invoke(message)
    return {"messages": [response]}

g.add_node("model", call_model)
from langgraph.graph import END
g.add_edge("model",END)
g.set_entry_point("model")
graph = g.compile()
print(graph.get_graph().draw_ascii())
while True:
    user_input = input("user :")
    if user_input in ["quit","q"]:
        print("exiting program")
        break
    print(graph.invoke({"messages": user_input}))
    




