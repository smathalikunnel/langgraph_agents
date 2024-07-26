from dotenv import load_dotenv
_ = load_dotenv()

from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")

class State(TypedDict):
    messages: Annotated[list,add_messages]

graph_builder = StateGraph(State)

def chatbot(state: State) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}
    
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
graph = graph_builder.compile()

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}):
        print("----------------------------EVENT--------------------")
        print(event)
        for value in event.values():
            
            print("Assistant:", value["messages"][-1].content)
