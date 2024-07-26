

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END

from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from dotenv import load_dotenv

_ = load_dotenv()

# create state
class State(TypedDict):
    messages : Annotated[list, add_messages]

model_openai = ChatOpenAI(model="gpt-3.5-turbo")
model_ant = ChatAnthropic(model_name="claude-2.1")

#create graph - with 2 models
models = {"openai": model_openai,
         "anthropic": model_ant}

graph = StateGraph(State)

def _call_llm(state: State, config):
    messages = state["messages"]

    if "sys_msg" in config["configurables"]:
        messages = [SystemMessage(content=config["configurables"].get("sys_msg"))] + messages
    model = models[config["configurables"].get("model","anthropic")]
    response = model.invoke(messages)
    return {"messages": [response]}
# add nodes
graph.add_node("llm", _call_llm)

# add edges
graph.add_edge("llm", END)

# initialise graph
graph.set_entry_point("llm")
graph = graph.compile()

#call with config
config = {"configurables": {"model":"openai"}}
print(graph.invoke({"messages":"hi"}, config))

# add system msg to config 
config = {"configurables":{"model":"openai", "sys_msg":"respond in french"}}
print(graph.invoke({"messages":"hi"}, config))
