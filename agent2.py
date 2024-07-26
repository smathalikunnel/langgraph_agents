from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from openai import OpenAI
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

_ = load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, streaming=True)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages":[response]}
# create a custom state object
# intantiate the graph with state

graph_builder = StateGraph(State) # instantiate graph with schema
#define start and end fns
graph_builder.add_node("llm",call_model)
graph_builder.set_entry_point("llm")
graph_builder.set_finish_point("llm")
#compile and run graph
app = graph_builder.compile()
# send inputs 

while True:
    user_input = input("user: " )
    if user_input.lower() in ["quit","q","exit"]:
        print("goodbye")
        break
    for event in app.stream({"messages": ("user",user_input)}):
        for value in event.values():
            # print(value["messages"])
            print("assistant:", value["messages"][-1].content)
# print(app.invoke({"messages": [{"role": "user", "content":"how are you"}]}))